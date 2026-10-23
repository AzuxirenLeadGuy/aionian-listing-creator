"""Custom exception types for the Aionian Listing Creator project."""


class AionianListingError(RuntimeError):
    """Base class for project-specific runtime errors."""


class InvalidInputDirectoryError(AionianListingError):
    """Raised when the configured input or output directory is invalid."""


class InvalidNoiaFileError(AionianListingError):
    """Raised when a `.noia` file is missing, unreadable, or malformed."""


class InvalidNoiaFormatError(AionianListingError):
    """Raised when a parsed line does not match the expected `.noia` format."""


class InvalidCrossReferenceFormatError(AionianListingError):
    """Raised when a cross-reference record is malformed."""


class InvalidOutputFormatError(AionianListingError):
    """Raised when serialization output parameters or structure are invalid."""
