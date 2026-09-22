"""Application-specific exceptions."""


class CompetencyIntelligenceError(Exception):
    """Base error for the application."""


class ConfigurationError(CompetencyIntelligenceError):
    """Raised when configuration cannot be validated."""


class ScanError(CompetencyIntelligenceError):
    """Raised when a source cannot be downloaded safely."""


class ExtractionError(CompetencyIntelligenceError):
    """Raised when an article cannot be extracted into evidence."""


class FrameworkImportError(CompetencyIntelligenceError):
    """Raised when a framework import cannot be validated."""


class RecommendationError(CompetencyIntelligenceError):
    """Raised when recommendations cannot be generated or validated."""


class ReviewError(CompetencyIntelligenceError):
    """Raised when an officer review action is invalid."""
