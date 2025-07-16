class DomainError(Exception):
    """Base exception for domain errors."""
    pass


class InvalidDocumentError(DomainError):
    """Raised when document is invalid."""
    pass


class DocumentNotFoundError(DomainError):
    """Raised when document cannot be found."""
    pass


class CorpusNotFoundError(DomainError):
    """Raised when corpus cannot be found."""
    pass


class CorpusAlreadyExistsError(DomainError):
    """Raised when trying to create a corpus that already exists."""
    pass


class RAGQueryError(DomainError):
    """Raised when RAG query fails."""
    pass