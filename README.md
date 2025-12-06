Title: Internal Travel Approval System (Django + DRF)

What it does
A role-based workflow system for travel requests with policy evaluation and multi-step approvals (manager + finance).

Roles

Employee: create draft, submit

Manager: approve/reject

Finance: approve escalations

Workflow

Employee creates DRAFT

Employee submits → policy runs

Status becomes PENDING_MANAGER or ESCALATED_FINANCE

Manager or Finance approves

System enforces state transitions and ownership

Built with

Django, Django REST Framework

SQLite (dev)

Router-driven ViewSets

Policy engine integration

Why this matters
Demonstrates:

API design

Authorization

Business rules enforcement

State machines

Defensive programming

Known limitation (dev mode)
Manager approval via Browsable API may 403 when switching users mid-session (CSRF/session context). Core API logic and permissions are intact.