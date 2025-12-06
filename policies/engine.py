from decimal import Decimal
from .models import PolicyRule


def evaluate_travel_request(travel_request):
    """
    Evaluates a TravelRequest against all TRAVEL rules.
    Returns a list of rule violations.
    """
    violations = []
    rules = PolicyRule.objects.filter(scope=PolicyRule.Scope.TRAVEL, active=True)

    for rule in rules:
        # Check cost thresholds
        if rule.min_amount is not None and travel_request.estimated_cost < rule.min_amount:
            continue

        if rule.max_amount is not None and travel_request.estimated_cost > rule.max_amount:
            continue

        # If we reached here, the rule applies
        violation = {
            "rule": rule.name,
            "require_finance_approval": rule.require_finance_approval,
            "auto_flag": rule.auto_flag,
        }
        violations.append(violation)

    return violations


def evaluate_expense(expense):
    """
    Evaluates an Expense against all EXPENSE rules.
    Returns a list of rule violations.
    """
    violations = []
    rules = PolicyRule.objects.filter(scope=PolicyRule.Scope.EXPENSE, active=True)

    for rule in rules:
        # Check amount thresholds
        if rule.min_amount is not None and expense.amount < Decimal(rule.min_amount):
            continue

        if rule.max_amount is not None and expense.amount > Decimal(rule.max_amount):
            continue

        violation = {
            "rule": rule.name,
            "require_finance_approval": rule.require_finance_approval,
            "auto_flag": rule.auto_flag,
        }
        violations.append(violation)

    return violations
