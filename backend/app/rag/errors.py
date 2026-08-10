class ProcessingError(Exception):
    """Permanent failure that must not be retried (bad file, corrupt data, unsupported type)."""


class RetryableError(Exception):
    """Transient failure (network, provider outage) that may be retried."""
