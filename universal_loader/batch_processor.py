"""
Batch processing functionality for Universal Data Loader
"""

import json
import time
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import fnmatch

from .loader import UniversalDataLoader
from .batch_config import BatchConfig, InputSource, InputType, OutputConfig
from .document import DocumentCollection, Document
from .config import LoaderConfig


class BatchProcessor:
    """Handles batch processing of multiple input sources"""
    
    def __init__(self, config: BatchConfig):
        """Initialize batch processor with configuration"""
        self.config = config
        self.batch_id = config.batch_id or self._generate_batch_id()
        self.results = {}
        self.errors = {}
        
    def _generate_batch_id(self) -> str:
        """Generate a unique batch ID"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"batch_{timestamp}"
    
    def process_all(self) -> Dict[str, Any]:
        """
        Process all sources in the batch configuration
        
        Returns:
            Dictionary with processing results and statistics
        """
        if self.config.verbose:
            print(f"🚀 Starting batch processing: {self.batch_id}")
            print(f"📋 Processing {len(self.config.sources)} sources")
        
        # Ensure output directory exists
        output_dir = Path(self.config.output.base_path)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Process sources
        if self.config.max_workers == 1:
            # Sequential processing
            self._process_sequential()
        else:
            # Parallel processing
            self._process_parallel()
        
        # Handle output generation
        output_files = self._generate_outputs()
        
        # Generate summary
        summary = self._generate_summary(output_files)
        
        if self.config.verbose:
            print(f"✅ Batch processing completed: {self.batch_id}")
            print(f"📊 Processed {summary['successful_sources']}/{summary['total_sources']} sources")
        
        return summary
    
    def _process_sequential(self):
        """Process sources sequentially"""
        for i, source in enumerate(self.config.sources):
            if self.config.verbose:
                print(f"📄 Processing source {i+1}/{len(self.config.sources)}: {source.path}")
            
            try:
                result = self._process_single_source(source)
                self.results[source.path] = result
            except Exception as e:
                self.errors[source.path] = str(e)
                if self.config.verbose:
                    print(f"❌ Error processing {source.path}: {e}")
                
                if not self.config.continue_on_error:
                    raise
    
    def _process_parallel(self):
        """Process sources in parallel"""
        with ThreadPoolExecutor(max_workers=self.config.max_workers) as executor:
            # Submit all tasks
            future_to_source = {
                executor.submit(self._process_single_source, source): source 
                for source in self.config.sources
            }
            
            # Collect results
            for future in as_completed(future_to_source):
                source = future_to_source[future]
                try:
                    result = future.result()
                    self.results[source.path] = result
                    if self.config.verbose:
                        print(f"✅ Completed: {source.path}")
                except Exception as e:
                    self.errors[source.path] = str(e)
                    if self.config.verbose:
                        print(f"❌ Error processing {source.path}: {e}")
                    
                    if not self.config.continue_on_error:
                        # Cancel remaining tasks and raise
                        for f in future_to_source:
                            f.cancel()
                        raise
    
    def _process_single_source(self, source: InputSource) -> DocumentCollection:
        """Process a single input source"""
        # Create loader with source-specific config
        loader_config = self._get_loader_config_for_source(source)
        loader = UniversalDataLoader(loader_config)
        
        # Process based on source type
        if source.type == InputType.FILE:
            documents = loader.load_file(source.path)
        elif source.type == InputType.DIRECTORY:
            documents = self._process_directory_with_patterns(loader, source)
        elif source.type == InputType.URL:
            documents = loader.load_url(source.path)
        else:
            raise ValueError(f"Unsupported source type: {source.type}")
        
        # Add batch metadata
        if self.config.add_batch_metadata:
            self._add_batch_metadata(documents, source)
        
        return documents
    
    def _get_loader_config_for_source(self, source: InputSource) -> LoaderConfig:
        """Get loader configuration for a specific source"""
        # Start with base config
        config_dict = self.config.loader_config.dict()
        
        # Apply source-specific overrides
        if source.custom_config:
            config_dict.update(source.custom_config)
        
        return LoaderConfig(**config_dict)
    
    def _process_directory_with_patterns(self, loader: UniversalDataLoader, source: InputSource) -> DocumentCollection:
        """Process directory with include/exclude patterns"""
        if not source.include_patterns and not source.exclude_patterns:
            # No patterns, use standard directory processing
            return loader.load_directory(source.path, recursive=source.recursive)
        
        # Custom processing with patterns
        directory_path = Path(source.path)
        all_documents = DocumentCollection()
        
        # Find files matching patterns
        if source.recursive:
            file_pattern = "**/*"
        else:
            file_pattern = "*"
        
        for file_path in directory_path.glob(file_pattern):
            if not file_path.is_file():
                continue
            
            file_name = file_path.name
            
            # Check include patterns
            if source.include_patterns:
                if not any(fnmatch.fnmatch(file_name, pattern) for pattern in source.include_patterns):
                    continue
            
            # Check exclude patterns
            if source.exclude_patterns:
                if any(fnmatch.fnmatch(file_name, pattern) for pattern in source.exclude_patterns):
                    continue
            
            # Process the file
            try:
                documents = loader.load_file(file_path)
                # Add source file metadata
                for doc in documents:
                    doc.add_metadata('source_file', str(file_path))
                all_documents.add_documents(documents.to_list())
            except Exception as e:
                if self.config.verbose:
                    print(f"⚠️ Warning: Failed to process {file_path}: {e}")
        
        return all_documents
    
    def _add_batch_metadata(self, documents: DocumentCollection, source: InputSource):
        """Add batch processing metadata to documents"""
        batch_metadata = {
            'batch_id': self.batch_id,
            'batch_source_type': source.type.value,
            'batch_source_path': source.path,
            'batch_processed_at': datetime.now().isoformat()
        }
        
        for doc in documents:
            doc.merge_metadata(batch_metadata)
    
    def _generate_outputs(self) -> Dict[str, str]:
        """Generate output files based on configuration"""
        output_files = {}
        
        if self.config.output.separate_by_source:
            # Create separate file for each source
            for source_path, documents in self.results.items():
                output_file = self._get_output_filename(source_path)
                self._save_documents(documents, output_file)
                output_files[source_path] = str(output_file)
        
        if self.config.output.merge_all:
            # Create merged file with all sources
            merged_documents = DocumentCollection()
            for documents in self.results.values():
                merged_documents.add_documents(documents.to_list())
            
            merged_file = Path(self.config.output.base_path) / f"{self.batch_id}_merged.json"
            self._save_documents(merged_documents, merged_file)
            output_files['merged'] = str(merged_file)
        
        return output_files
    
    def _get_output_filename(self, source_path: str) -> Path:
        """Generate output filename for a source"""
        # Find the source configuration
        source_config = None
        for source in self.config.sources:
            if source.path == source_path:
                source_config = source
                break
        
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if source_config and source_config.output_prefix:
            source_name = source_config.output_prefix
        else:
            # Generate from path
            if source_path.startswith(('http://', 'https://')):
                source_name = "url_" + source_path.split('/')[-1].split('.')[0]
            else:
                source_name = Path(source_path).stem
        
        # Apply template
        filename = self.config.output.filename_template.format(
            source_name=source_name,
            timestamp=timestamp,
            batch_id=self.batch_id
        )
        
        return Path(self.config.output.base_path) / f"{filename}.json"
    
    def _save_documents(self, documents: DocumentCollection, output_path: Path):
        """Save documents to file"""
        # Use the loader's save functionality
        temp_loader = UniversalDataLoader(self.config.loader_config)
        temp_loader.save_output(documents, output_path)
    
    def _generate_summary(self, output_files: Dict[str, str]) -> Dict[str, Any]:
        """Generate processing summary"""
        total_documents = 0
        total_words = 0
        total_characters = 0
        
        for documents in self.results.values():
            stats = documents.get_statistics()
            total_documents += stats['document_count']
            total_words += stats['total_words']
            total_characters += stats['total_characters']
        
        return {
            'batch_id': self.batch_id,
            'processed_at': datetime.now().isoformat(),
            'total_sources': len(self.config.sources),
            'successful_sources': len(self.results),
            'failed_sources': len(self.errors),
            'total_documents': total_documents,
            'total_words': total_words,
            'total_characters': total_characters,
            'output_files': output_files,
            'errors': self.errors,
            'processing_config': {
                'max_workers': self.config.max_workers,
                'continue_on_error': self.config.continue_on_error,
                'merge_all': self.config.output.merge_all,
                'separate_by_source': self.config.output.separate_by_source
            }
        }


def process_batch_from_config_file(config_file_path: Union[str, Path]) -> Dict[str, Any]:
    """
    Process batch from a configuration file
    
    Args:
        config_file_path: Path to JSON configuration file
        
    Returns:
        Processing summary
    """
    config_path = Path(config_file_path)
    
    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    
    # Load configuration
    with open(config_path, 'r', encoding='utf-8') as f:
        config_dict = json.load(f)
    
    # Create batch configuration
    batch_config = BatchConfig(**config_dict)
    
    # Process batch
    processor = BatchProcessor(batch_config)
    return processor.process_all()


def process_urls_batch(
    urls: List[str],
    output_dir: str = "url_batch_output",
    max_workers: int = 3,
    verbose: bool = True
) -> Dict[str, Any]:
    """
    Quick batch processing of multiple URLs
    
    Args:
        urls: List of URLs to process
        output_dir: Directory for output files
        max_workers: Number of parallel workers
        verbose: Verbose output
        
    Returns:
        Processing summary
    """
    from .batch_config import create_url_batch_config
    
    # Create configuration
    config = create_url_batch_config(urls, output_dir)
    config.max_workers = max_workers
    config.verbose = verbose
    
    # Process batch
    processor = BatchProcessor(config)
    return processor.process_all()


def process_directories_batch(
    directories: List[str],
    output_dir: str = "directory_batch_output",
    recursive: bool = True,
    max_workers: int = 2,
    verbose: bool = True
) -> Dict[str, Any]:
    """
    Quick batch processing of multiple directories
    
    Args:
        directories: List of directory paths
        output_dir: Directory for output files
        recursive: Process directories recursively
        max_workers: Number of parallel workers
        verbose: Verbose output
        
    Returns:
        Processing summary
    """
    from .batch_config import create_directory_batch_config
    
    # Create configuration
    config = create_directory_batch_config(directories, output_dir, recursive)
    config.max_workers = max_workers
    config.verbose = verbose
    
    # Process batch
    processor = BatchProcessor(config)
    return processor.process_all()