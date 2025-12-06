from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import TravelRequest
from .serializers import TravelRequestSerializer


class TravelRequestViewSet(viewsets.ModelViewSet):
    serializer_class = TravelRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    # ------------------ QUERYSET PER ROLE ------------------

    def get_queryset(self):
        user = self.request.user
        qs = TravelRequest.objects.all()

        # If user has no profile for some reason, be safe and show nothing
        if not hasattr(user, "profile"):
            return qs.none()

        role = user.profile.role

        if role == "EMPLOYEE":
            # Employees see only their own requests
            return qs.filter(employee=user)

        if role == "MANAGER":
            # Managers see only items waiting for manager approval
            return qs.filter(status=TravelRequest.Status.PENDING_MANAGER)

        if role == "FINANCE":
            # Finance sees only escalated items
            return qs.filter(status=TravelRequest.Status.ESCALATED_FINANCE)

        # Default: nothing
        return qs.none()

    def perform_create(self, serializer):
        """
        New travel requests start as DRAFT owned by the current user.
        Policy checks are run on SUBMIT, not on raw creation.
        """
        serializer.save(employee=self.request.user)

    # --------- Small helpers for role checks ---------

    def _is_manager(self, user):
        return hasattr(user, "profile") and user.profile.role == "MANAGER"

    def _is_finance(self, user):
        return hasattr(user, "profile") and user.profile.role == "FINANCE"

    def _is_employee(self, user):
        return hasattr(user, "profile") and user.profile.role == "EMPLOYEE"

    # ------------------ SUBMIT (DRAFT → workflow) ------------------

    @action(detail=True, methods=["post"])
    def submit(self, request, pk=None):
        """
        Employee submits a draft request into the approval workflow.

        - Only the owner can submit
        - Only DRAFT requests can be submitted
        - Policies are evaluated here
        - Resulting status:
            - ESCALATED_FINANCE (if policies demand it)
            - PENDING_MANAGER (normal path)
        """
        user = request.user
        obj = self.get_object()

        # Only owner can submit
        if obj.employee != user:
            return Response(
                {"error": "You can only submit your own travel requests."},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Only DRAFT can be submitted
        if obj.status != TravelRequest.Status.DRAFT:
            return Response(
                {"error": f"Only DRAFT requests can be submitted (current: {obj.status})."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Run policies — this may change status internally to ESCALATED_FINANCE
        violations = obj.run_policy_checks()

        # If policy engine escalated, status is already ESCALATED_FINANCE.
        # Otherwise we send it to the manager.
        if obj.status == TravelRequest.Status.DRAFT:
            obj.status = TravelRequest.Status.PENDING_MANAGER
            obj.save()

        return Response(
            {
                "status": obj.status,
                "policy_flags": obj.policy_flags,
                "violations": violations,
            },
            status=status.HTTP_200_OK,
        )

    # ------------------ LOCK EDITS AFTER SUBMISSION ------------------

    def _ensure_editable(self, request, obj):
        """
        Only allow editing/deleting while in DRAFT and owned by the user.
        Returns a Response if blocked, or None if allowed.
        """
        user = request.user

        if obj.status != TravelRequest.Status.DRAFT:
            return Response(
                {"error": "Only DRAFT requests can be modified or deleted."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if obj.employee != user:
            return Response(
                {"error": "You can only modify your own travel requests."},
                status=status.HTTP_403_FORBIDDEN,
            )

        return None

    def update(self, request, *args, **kwargs):
        obj = self.get_object()
        blocked = self._ensure_editable(request, obj)
        if blocked:
            return blocked
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        obj = self.get_object()
        blocked = self._ensure_editable(request, obj)
        if blocked:
            return blocked
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        obj = self.get_object()
        blocked = self._ensure_editable(request, obj)
        if blocked:
            return blocked
        return super().destroy(request, *args, **kwargs)

    # ------------------ MANAGER APPROVAL ------------------

    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        user = request.user
        obj = self.get_object()

        # Must be manager
        if not self._is_manager(user):
            return Response(
                {"error": "Only managers can approve requests."},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Manager cannot approve own request
        if obj.employee == user:
            return Response(
                {"error": "You cannot approve your own travel request."},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Only PENDING_MANAGER can be manager-approved
        if obj.status != TravelRequest.Status.PENDING_MANAGER:
            return Response(
                {"error": f"Cannot approve request in '{obj.status}' state."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        obj.status = TravelRequest.Status.APPROVED
        obj.manager = user
        obj.save()

        return Response(
            {"status": "approved", "approved_by": user.username},
            status=status.HTTP_200_OK,
        )

    # ------------------ MANAGER REJECTION ------------------

    @action(detail=True, methods=["post"])
    def reject(self, request, pk=None):
        user = request.user
        obj = self.get_object()

        if not self._is_manager(user):
            return Response(
                {"error": "Only managers can reject requests."},
                status=status.HTTP_403_FORBIDDEN,
            )

        if obj.employee == user:
            return Response(
                {"error": "You cannot reject your own travel request."},
                status=status.HTTP_403_FORBIDDEN,
            )

        if obj.status != TravelRequest.Status.PENDING_MANAGER:
            return Response(
                {"error": f"Cannot reject request in '{obj.status}' state."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        obj.status = TravelRequest.Status.REJECTED
        obj.manager = user
        obj.save()

        return Response(
            {"status": "rejected", "rejected_by": user.username},
            status=status.HTTP_200_OK,
        )

    # ------------------ FINANCE APPROVAL ------------------

    @action(detail=True, methods=["post"])
    def finance_approve(self, request, pk=None):
        user = request.user
        obj = self.get_object()

        if not self._is_finance(user):
            return Response(
                {"error": "Only finance can approve escalated requests."},
                status=status.HTTP_403_FORBIDDEN,
            )

        if obj.status != TravelRequest.Status.ESCALATED_FINANCE:
            return Response(
                {
                    "error": (
                        "Finance can only approve requests that have been "
                        "escalated (ESCALATED_FINANCE), not "
                        f"'{obj.status}'."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        obj.status = TravelRequest.Status.APPROVED
        obj.finance_reviewer = user
        obj.save()

        return Response(
            {"status": "finance approved", "approved_by": user.username},
            status=status.HTTP_200_OK,
        )

    @action(detail=False, methods=["get"])
    def whoami(self, request):
        role = getattr(getattr(request.user, "profile", None), "role", None)
        return Response({"user": request.user.username, "role": role})

