"""Query engine models."""

from ..models.common import CaseInsensitiveEnum


class QueryEngines(CaseInsensitiveEnum):
    """Enumeration of possible query engines."""

    DIRECT_BUTLER = "DIRECT_BUTLER"
    REMOTE_BUTLER = "REMOTE_BUTLER"
