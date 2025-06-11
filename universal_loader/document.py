"""
Document classes compatible with LangChain and other LLM frameworks
"""

from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field


class Document(BaseModel):
    """
    Document class compatible with LangChain's Document format.
    
    This class represents a piece of text and its associated metadata,
    following the LangChain Document structure for maximum compatibility.
    """
    
    page_content: str = Field(description="The main text content of the document")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadata associated with the document")
    
    def __init__(self, page_content: str, metadata: Optional[Dict[str, Any]] = None, **kwargs):
        """
        Initialize a Document.
        
        Args:
            page_content: The main text content
            metadata: Dictionary of metadata about the document
            **kwargs: Additional keyword arguments
        """
        if metadata is None:
            metadata = {}
        super().__init__(page_content=page_content, metadata=metadata, **kwargs)
    
    def __str__(self) -> str:
        """Return the page content when converted to string"""
        return self.page_content
    
    def __repr__(self) -> str:
        """Return a detailed representation of the document"""
        metadata_str = str(self.metadata) if self.metadata else "{}"
        content_preview = self.page_content[:100] + "..." if len(self.page_content) > 100 else self.page_content
        return f"Document(page_content='{content_preview}', metadata={metadata_str})"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the document to a dictionary"""
        return {
            "page_content": self.page_content,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Document":
        """Create a Document from a dictionary"""
        return cls(
            page_content=data.get("page_content", ""),
            metadata=data.get("metadata", {})
        )
    
    def add_metadata(self, key: str, value: Any) -> None:
        """Add a metadata field to the document"""
        self.metadata[key] = value
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """Get a metadata field from the document"""
        return self.metadata.get(key, default)
    
    def has_metadata(self, key: str) -> bool:
        """Check if a metadata field exists"""
        return key in self.metadata
    
    def remove_metadata(self, key: str) -> bool:
        """Remove a metadata field. Returns True if removed, False if not found"""
        if key in self.metadata:
            del self.metadata[key]
            return True
        return False
    
    def clone(self) -> "Document":
        """Create a copy of the document"""
        return Document(
            page_content=self.page_content,
            metadata=self.metadata.copy()
        )
    
    def merge_metadata(self, other_metadata: Dict[str, Any]) -> None:
        """Merge additional metadata into this document"""
        self.metadata.update(other_metadata)


class DocumentCollection:
    """
    A collection of documents with utility methods for batch operations.
    Useful for handling multiple documents from directory processing or chunking.
    """
    
    def __init__(self, documents: Optional[List[Document]] = None):
        """Initialize with optional list of documents"""
        self.documents = documents or []
    
    def add_document(self, document: Document) -> None:
        """Add a document to the collection"""
        self.documents.append(document)
    
    def add_documents(self, documents: List[Document]) -> None:
        """Add multiple documents to the collection"""
        self.documents.extend(documents)
    
    def __len__(self) -> int:
        """Return the number of documents"""
        return len(self.documents)
    
    def __iter__(self):
        """Make the collection iterable"""
        return iter(self.documents)
    
    def __getitem__(self, index: int) -> Document:
        """Allow indexing into the collection"""
        return self.documents[index]
    
    def filter_by_metadata(self, key: str, value: Any) -> "DocumentCollection":
        """Filter documents by a metadata field value"""
        filtered_docs = [doc for doc in self.documents if doc.get_metadata(key) == value]
        return DocumentCollection(filtered_docs)
    
    def filter_by_content_length(self, min_length: int = 0, max_length: int = float('inf')) -> "DocumentCollection":
        """Filter documents by content length"""
        filtered_docs = [
            doc for doc in self.documents 
            if min_length <= len(doc.page_content) <= max_length
        ]
        return DocumentCollection(filtered_docs)
    
    def get_metadata_values(self, key: str) -> List[Any]:
        """Get all unique values for a metadata key across all documents"""
        values = []
        for doc in self.documents:
            if doc.has_metadata(key):
                value = doc.get_metadata(key)
                if value not in values:
                    values.append(value)
        return values
    
    def to_list(self) -> List[Document]:
        """Return the documents as a list"""
        return self.documents.copy()
    
    def to_dicts(self) -> List[Dict[str, Any]]:
        """Convert all documents to dictionaries"""
        return [doc.to_dict() for doc in self.documents]
    
    def get_total_content_length(self) -> int:
        """Get the total character count across all documents"""
        return sum(len(doc.page_content) for doc in self.documents)
    
    def get_total_word_count(self) -> int:
        """Get the total word count across all documents"""
        return sum(len(doc.page_content.split()) for doc in self.documents)
    
    def merge_all(self, separator: str = "\n\n") -> Document:
        """Merge all documents into a single document"""
        if not self.documents:
            return Document(page_content="", metadata={})
        
        # Combine all page content
        combined_content = separator.join(doc.page_content for doc in self.documents)
        
        # Merge metadata (later documents override earlier ones for conflicts)
        combined_metadata = {}
        for doc in self.documents:
            combined_metadata.update(doc.metadata)
        
        # Add collection metadata
        combined_metadata["document_count"] = len(self.documents)
        combined_metadata["merged_from_collection"] = True
        
        return Document(page_content=combined_content, metadata=combined_metadata)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about the document collection"""
        if not self.documents:
            return {
                "document_count": 0,
                "total_characters": 0,
                "total_words": 0,
                "average_characters": 0,
                "average_words": 0,
                "metadata_keys": []
            }
        
        total_chars = self.get_total_content_length()
        total_words = self.get_total_word_count()
        doc_count = len(self.documents)
        
        # Get all unique metadata keys
        all_metadata_keys = set()
        for doc in self.documents:
            all_metadata_keys.update(doc.metadata.keys())
        
        return {
            "document_count": doc_count,
            "total_characters": total_chars,
            "total_words": total_words,
            "average_characters": total_chars / doc_count,
            "average_words": total_words / doc_count,
            "metadata_keys": sorted(list(all_metadata_keys))
        }