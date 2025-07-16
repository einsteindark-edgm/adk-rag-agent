from typing import List, Optional, Dict, Any
from datetime import datetime


class Corpus:
    """Domain entity representing a document corpus.
    
    This entity represents a collection of documents with metadata.
    """
    
    def __init__(self, name: str, display_name: Optional[str] = None, 
                 description: Optional[str] = None):
        """Initialize corpus with validation.
        
        Args:
            name: Unique name of the corpus
            display_name: Human-readable display name
            description: Description of corpus contents
            
        Raises:
            ValueError: If name is invalid
        """
        if not name or not name.strip():
            raise ValueError("Corpus name cannot be empty")
        
        self.name = name.strip()
        self.display_name = display_name or name
        self.description = description
        self.document_count = 0
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def update_document_count(self, count: int) -> None:
        """Update the document count.
        
        Args:
            count: New document count
            
        Raises:
            ValueError: If count is negative
        """
        if count < 0:
            raise ValueError("Document count cannot be negative")
        
        self.document_count = count
        self.updated_at = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "name": self.name,
            "display_name": self.display_name,
            "description": self.description,
            "document_count": self.document_count,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }