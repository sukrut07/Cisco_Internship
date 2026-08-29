"""
NetSage AI — ORM Models Package.

Importing this package ensures all models are registered with SQLAlchemy's
metadata before Alembic generates migrations.
"""
from app.models.case import Case
from app.models.diagnosis import Diagnosis
from app.models.rule_result import RuleResult
from app.models.review import Review
from app.models.verification import Verification
from app.models.audit import AuditLog


def _import_all_models() -> None:
    """Dummy function to ensure all models are imported (used by database.py)."""
    pass


__all__ = [
    "Case",
    "Diagnosis",
    "RuleResult",
    "Review",
    "Verification",
    "AuditLog",
]
