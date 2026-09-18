"""Network-capable source adapters.

Only modules in this package may retrieve remote source data. Consumers pass
cached bytes or normalized values into calculation and rendering modules.
"""

from .adapters import SourceValidationError
from .snapshot import SnapshotError, acquire_snapshot, resolve_current, verify_snapshot

__all__ = [
    "SnapshotError",
    "SourceValidationError",
    "acquire_snapshot",
    "resolve_current",
    "verify_snapshot",
]
