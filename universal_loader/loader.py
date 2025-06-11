"""
Universal Data Loader implementation
"""

import os
import json
from pathlib import Path
from typing import List, Dict, Any, Union, Optional
from urllib.parse import urlparse

from unstructured.partition.auto import partition
from unstructured.partition.pdf import partition_pdf
from unstructured.partition.docx import partition_docx
from unstructured.partition.html import partition_html
from unstructured.partition.text import partition_text
from unstructured.partition.csv import partition_csv
from unstructured.partition.xlsx import partition_xlsx
from unstructured.partition.pptx import partition_pptx
from unstructured.partition.email import partition_email
from unstructured.chunking.title import chunk_by_title
from unstructured.chunking.basic import chunk_elements
from unstructured.staging.base import elements_to_json, convert_to_dict

from .config import LoaderConfig, OutputFormat, ChunkingStrategy
from .document import Document, DocumentCollection


class UniversalDataLoader:
    """Universal data loader that can process multiple file types using Unstructured"""

    SUPPORTED_EXTENSIONS = {
        '.pdf', '.docx', '.doc', '.html', '.htm', '.txt', '.md',
        '.csv', '.xlsx', '.xls', '.pptx', '.ppt', '.eml', '.msg',
        '.xml', '.json', '.rtf'
    }

    def __init__(self, config: Optional[LoaderConfig] = None):
        """Initialize the loader with configuration"""
        self.config = config or LoaderConfig()
        
    def load_file(self, file_path: Union[str, Path]) -> Union[List[Dict[str, Any]], List[Document], DocumentCollection]:
        """
        Load and process a single file
        
        Args:
            file_path: Path to the file to process
            
        Returns:
            Processed documents in the format specified by config.output_format:
            - DOCUMENTS: DocumentCollection with Document objects (default)
            - JSON: List of dictionaries
            - TEXT: List of text dictionaries 
            - ELEMENTS: Raw unstructured elements
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
            
        if file_path.suffix.lower() not in self.SUPPORTED_EXTENSIONS:
            raise ValueError(f"Unsupported file type: {file_path.suffix}")
            
        # Partition the document based on file type
        elements = self._partition_file(file_path)
        
        # Apply processing steps
        if self.config.remove_headers_footers:
            elements = self._remove_headers_footers(elements)
            
        if self.config.min_text_length > 0:
            elements = self._filter_by_length(elements)
            
        # Apply chunking if specified
        if self.config.chunking_strategy:
            elements = self._apply_chunking(elements)
            
        # Convert to desired output format
        return self._format_output(elements)
        
    def load_directory(self, directory_path: Union[str, Path], 
                      recursive: bool = True) -> Union[List[Dict[str, Any]], List[Document], DocumentCollection]:
        """
        Load and process all supported files in a directory
        
        Args:
            directory_path: Path to the directory
            recursive: Whether to search subdirectories
            
        Returns:
            Processed documents from all files in the format specified by config.output_format
        """
        directory_path = Path(directory_path)
        
        if not directory_path.exists():
            raise FileNotFoundError(f"Directory not found: {directory_path}")
            
        all_documents = DocumentCollection() if self.config.output_format == OutputFormat.DOCUMENTS else []
        
        if recursive:
            file_pattern = "**/*"
        else:
            file_pattern = "*"
            
        for file_path in directory_path.glob(file_pattern):
            if (file_path.is_file() and 
                file_path.suffix.lower() in self.SUPPORTED_EXTENSIONS):
                try:
                    result = self.load_file(file_path)
                    
                    if self.config.output_format == OutputFormat.DOCUMENTS:
                        # result is a DocumentCollection, add its documents
                        for doc in result:
                            doc.add_metadata('source_file', str(file_path))
                        all_documents.add_documents(result.to_list())
                    else:
                        # result is a list, add source file metadata and extend
                        for element in result:
                            if isinstance(element, dict):
                                element['source_file'] = str(file_path)
                        all_documents.extend(result)
                        
                except Exception as e:
                    print(f"Warning: Failed to process {file_path}: {e}")
                    
        return all_documents
        
    def load_url(self, url: str) -> Union[List[Dict[str, Any]], List[Document], DocumentCollection]:
        """
        Load and process content from a URL
        
        Args:
            url: URL to process
            
        Returns:
            Processed documents in the format specified by config.output_format
        """
        # Use unstructured's URL handling
        elements = partition(url=url, **self.config.custom_partition_kwargs)
        
        # Apply processing steps
        if self.config.remove_headers_footers:
            elements = self._remove_headers_footers(elements)
            
        if self.config.min_text_length > 0:
            elements = self._filter_by_length(elements)
            
        if self.config.chunking_strategy:
            elements = self._apply_chunking(elements)
            
        return self._format_output(elements)

    def _create_combined_documents(self, elements) -> DocumentCollection:
        """
        Create combined documents without aggressive chunking.
        Groups elements intelligently to preserve context.
        """
        documents = DocumentCollection()
        
        # Group elements by source (page, section, or document)
        grouped_elements = self._group_elements_by_source(elements)
        
        for group_key, group_elements in grouped_elements.items():
            # Combine all text from elements in this group
            combined_text = []
            combined_metadata = {}
            element_types = set()
            
            for element in group_elements:
                text = str(element).strip()
                if text and len(text) >= self.config.min_text_length:
                    combined_text.append(text)
                    
                    # Collect metadata from first element or common metadata
                    if not combined_metadata and self.config.include_metadata:
                        if hasattr(element, 'metadata') and element.metadata:
                            if hasattr(element.metadata, 'to_dict'):
                                combined_metadata.update(element.metadata.to_dict())
                            elif isinstance(element.metadata, dict):
                                combined_metadata.update(element.metadata)
                    
                    # Track element types
                    if hasattr(element, 'category'):
                        element_types.add(element.category)
            
            # Create combined document if we have content
            if combined_text:
                page_content = '\n\n'.join(combined_text)
                
                # Add summary metadata
                if self.config.include_metadata:
                    combined_metadata['element_types'] = list(element_types)
                    combined_metadata['combined_elements_count'] = len(combined_text)
                    if not combined_metadata.get('element_type'):
                        combined_metadata['element_type'] = 'Combined'
                
                doc = Document(page_content=page_content, metadata=combined_metadata)
                documents.add_document(doc)
        
        return documents

    def _group_elements_by_source(self, elements):
        """Group elements by source (page, file, or logical section)"""
        groups = {}
        
        for element in elements:
            # Try to group by page number first
            group_key = 'page_1'  # default
            
            if hasattr(element, 'metadata') and element.metadata:
                metadata = element.metadata
                if hasattr(metadata, 'to_dict'):
                    meta_dict = metadata.to_dict()
                elif isinstance(metadata, dict):
                    meta_dict = metadata
                else:
                    meta_dict = {}
                
                # Group by page number if available
                page_num = meta_dict.get('page_number', meta_dict.get('page', 1))
                group_key = f'page_{page_num}'
                
                # For web content, group by URL or document
                if 'url' in meta_dict:
                    group_key = f"url_{meta_dict['url']}"
                elif 'filename' in meta_dict:
                    group_key = f"file_{meta_dict['filename']}"
            
            if group_key not in groups:
                groups[group_key] = []
            groups[group_key].append(element)
        
        return groups

    def _create_chunked_documents(self, elements) -> DocumentCollection:
        """
        Create documents with chunking strategy applied.
        This preserves the original behavior when chunking is explicitly requested.
        """
        documents = DocumentCollection()
        
        # For chunked documents, use original element-per-document approach
        for element in elements:
            text_content = str(element)
            if len(text_content) < self.config.min_text_length:
                continue
                
            metadata = {}
            if self.config.include_metadata:
                if hasattr(element, 'category'):
                    metadata['element_type'] = element.category
                if hasattr(element, 'metadata') and element.metadata:
                    if hasattr(element.metadata, 'to_dict'):
                        metadata.update(element.metadata.to_dict())
                    elif isinstance(element.metadata, dict):
                        metadata.update(element.metadata)
                if hasattr(element, 'id'):
                    metadata['element_id'] = element.id
            
            doc = Document(page_content=text_content, metadata=metadata)
            documents.add_document(doc)
        
        return documents
        
    def _partition_file(self, file_path: Path):
        """Partition a file based on its type"""
        file_ext = file_path.suffix.lower()
        
        # Common partition kwargs
        partition_kwargs = {
            'include_metadata': self.config.include_metadata,
            **self.config.custom_partition_kwargs
        }
        
        # Add OCR settings for relevant file types
        if file_ext == '.pdf':
            partition_kwargs.update({
                'languages': self.config.ocr_languages,
                'extract_images_in_pdf': self.config.extract_images
            })
            return partition_pdf(filename=str(file_path), **partition_kwargs)
            
        elif file_ext in ['.docx', '.doc']:
            return partition_docx(filename=str(file_path), **partition_kwargs)
            
        elif file_ext in ['.html', '.htm']:
            return partition_html(filename=str(file_path), **partition_kwargs)
            
        elif file_ext in ['.txt', '.md']:
            return partition_text(filename=str(file_path), **partition_kwargs)
            
        elif file_ext == '.csv':
            return partition_csv(filename=str(file_path), **partition_kwargs)
            
        elif file_ext in ['.xlsx', '.xls']:
            return partition_xlsx(filename=str(file_path), **partition_kwargs)
            
        elif file_ext in ['.pptx', '.ppt']:
            return partition_pptx(filename=str(file_path), **partition_kwargs)
            
        elif file_ext in ['.eml', '.msg']:
            return partition_email(filename=str(file_path), **partition_kwargs)
            
        else:
            # Use auto-partition for other types
            return partition(filename=str(file_path), **partition_kwargs)
            
    def _remove_headers_footers(self, elements):
        """Remove header and footer elements"""
        filtered_elements = []
        for element in elements:
            # Check if element has category attribute
            if hasattr(element, 'category'):
                if element.category not in ['Header', 'Footer']:
                    filtered_elements.append(element)
            else:
                filtered_elements.append(element)
        return filtered_elements
        
    def _filter_by_length(self, elements):
        """Filter elements by minimum text length"""
        filtered_elements = []
        for element in elements:
            text = str(element) if hasattr(element, '__str__') else ''
            if len(text.strip()) >= self.config.min_text_length:
                filtered_elements.append(element)
        return filtered_elements
        
    def _apply_chunking(self, elements):
        """Apply chunking strategy to elements"""
        if self.config.chunking_strategy == ChunkingStrategy.BY_TITLE:
            return chunk_by_title(
                elements,
                max_characters=self.config.max_chunk_size,
                overlap=self.config.chunk_overlap
            )
        elif self.config.chunking_strategy == ChunkingStrategy.BASIC:
            return chunk_elements(
                elements,
                max_characters=self.config.max_chunk_size,
                overlap=self.config.chunk_overlap
            )
        else:
            # For other strategies, implement basic chunking
            return chunk_elements(
                elements,
                max_characters=self.config.max_chunk_size,
                overlap=self.config.chunk_overlap
            )
            
    def _format_output(self, elements) -> Union[List[Dict[str, Any]], DocumentCollection]:
        """Format elements according to output configuration"""
        if self.config.output_format == OutputFormat.ELEMENTS:
            return elements
            
        elif self.config.output_format == OutputFormat.DOCUMENTS:
            # Convert elements to LangChain-compatible Documents
            documents = DocumentCollection()
            
            # Check if chunking is enabled
            if self.config.chunking_strategy:
                # Chunking enabled - use chunking strategy
                return self._create_chunked_documents(elements)
            else:
                # No chunking - combine elements intelligently
                return self._create_combined_documents(elements)
            
        elif self.config.output_format == OutputFormat.TEXT:
            text_elements = []
            for element in elements:
                text_elements.append({
                    'text': str(element),
                    'type': getattr(element, 'category', 'Unknown') if hasattr(element, 'category') else 'Unknown'
                })
            return text_elements
            
        else:  # JSON format
            return convert_to_dict(elements)
            
    def save_output(self, data: Union[List[Dict[str, Any]], DocumentCollection], 
                   output_path: Union[str, Path]) -> None:
        """
        Save processed data to file
        
        Args:
            data: Processed data to save (documents, elements, or dicts)
            output_path: Path to save the output
        """
        output_path = Path(output_path)
        
        if isinstance(data, DocumentCollection):
            # Handle DocumentCollection
            if self.config.output_format == OutputFormat.DOCUMENTS:
                # Save as JSON representation of documents
                docs_data = data.to_dicts()
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(docs_data, f, indent=2, ensure_ascii=False)
            else:
                # Save as text
                with open(output_path, 'w', encoding='utf-8') as f:
                    for doc in data:
                        f.write(f"{doc.page_content}\n\n")
        elif self.config.output_format == OutputFormat.JSON:
            # Handle list of dicts
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        else:
            # Handle other formats
            with open(output_path, 'w', encoding='utf-8') as f:
                for element in data:
                    if isinstance(element, dict):
                        f.write(f"{element.get('text', '')}\n\n")
                    else:
                        f.write(f"{element}\n\n")