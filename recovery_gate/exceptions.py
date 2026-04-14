class RecoveryGateError(Exception):
    """Base error for Recovery Gate."""

class VerificationError(RecoveryGateError):
    """Raised when invariant verification fails."""

class ApplyError(RecoveryGateError):
    """Raised when the apply step throws."""

class SnapshotError(RecoveryGateError):
    """Raised when snapshot/restore fails."""
