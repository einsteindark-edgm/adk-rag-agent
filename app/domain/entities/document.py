from typing import Optional
from datetime import datetime


class Document:
    """Domain entity representing a document.
    
    CRITICAL: This is a domain entity, not a data transfer object.
    It contains business logic and validation.
    """
    
    def __init__(self, filename: str, content: str, corpus_name: Optional[str] = None):
        """Initialize document with validation.
        
        Args:
            filename: Name of the document file
            content: Text content of the document
            corpus_name: Name of the corpus this document belongs to
            
        Raises:
            ValueError: If filename or content is invalid
        """
        if not filename or not filename.strip():
            raise ValueError("Document filename cannot be empty")
        
        if not content or not content.strip():
            raise ValueError("Document content cannot be empty")
        
        self.filename = filename.strip()
        self.content = content.strip()
        self.corpus_name = corpus_name
        self.created_at = datetime.utcnow()
    
    def is_empty(self) -> bool:
        """Check if document has no meaningful content."""
        return len(self.content.strip()) == 0
    
    def exceeds_size_limit(self, limit_kb: int = 350) -> bool:
        """Check if document exceeds size limit.
        
        BUSINESS RULE: Documents over 350KB may cause token limit issues.
        """
        size_kb = self.get_size_kb()
        return size_kb > limit_kb
    
    def get_size_kb(self) -> float:
        """Get document size in KB."""
        return len(self.content.encode('utf-8')) / 1024