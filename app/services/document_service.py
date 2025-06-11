"""
Document Processing Service
Core service for processing documents using the Universal Data Loader
"""

import json
from typing import Dict, Any, List
from pathlib import Path

from app.core.config import LoaderConfig, OutputFormat, ChunkingStrategy
from app.core.loader import UniversalDataLoader
from app.services.job_service import update_job_status, get_result_file_path


class DocumentProcessingService:
    """Service for processing documents"""
    
    @staticmethod
    def create_loader_config(config_data: Dict[str, Any]) -> LoaderConfig:
        """Create LoaderConfig from request data"""
        config_dict = {
            "output_format": OutputFormat(config_data.get("output_format", "documents")),
            "include_metadata": config_data.get("include_metadata", True),
            "min_text_length": config_data.get("min_text_length", 10),
            "remove_headers_footers": config_data.get("remove_headers_footers", True),
            "ocr_languages": config_data.get("ocr_languages", ["eng"])
        }
        
        # Only add chunking parameters if enable_chunking=True
        if config_data.get("enable_chunking", False):
            if not config_data.get("chunking_strategy"):
                raise ValueError("chunking_strategy is required when enable_chunking=True")
            if not config_data.get("max_chunk_size"):
                raise ValueError("max_chunk_size is required when enable_chunking=True")
                
            config_dict["chunking_strategy"] = ChunkingStrategy(config_data["chunking_strategy"])
            config_dict["max_chunk_size"] = config_data["max_chunk_size"]
            
            if config_data.get("chunk_overlap") is not None:
                config_dict["chunk_overlap"] = config_data["chunk_overlap"]
        
        return LoaderConfig(**config_dict)
    
    @staticmethod
    def _process_url_list(loader, file_path: str, source_data: Dict[str, Any]):
        """Process multiple URLs from a text file"""
        from pathlib import Path
        
        file_path_obj = Path(file_path)
        if not file_path_obj.exists():
            raise FileNotFoundError(f"URL list file not found: {file_path}")
        
        # Read URLs from file
        with open(file_path_obj, 'r', encoding='utf-8') as f:
            urls = [line.strip() for line in f if line.strip() and not line.strip().startswith('#')]
        
        if not urls:
            print(f"⚠️ No URLs found in file: {file_path}")
            return []
        
        print(f"📋 Processing {len(urls)} URLs from {file_path}")
        
        all_documents = []
        failed_urls = []
        
        for i, url in enumerate(urls):
            try:
                print(f"   🔗 Processing URL {i+1}/{len(urls)}: {url}")
                documents = loader.load_url(url)
                
                # Convert to standard format and add metadata
                if hasattr(documents, 'to_dicts'):
                    doc_list = documents.to_dicts()
                elif isinstance(documents, list):
                    doc_list = documents
                else:
                    doc_list = [documents] if documents else []
                
                # Add URL list metadata
                for doc in doc_list:
                    if isinstance(doc, dict):
                        doc['metadata'] = doc.get('metadata', {})
                        doc['metadata']['url_list_source'] = file_path
                        doc['metadata']['url_index'] = i + 1
                        doc['metadata']['source_url'] = url
                        if source_data.get('output_prefix'):
                            doc['metadata']['output_prefix'] = source_data['output_prefix']
                
                all_documents.extend(doc_list)
                print(f"      ✅ Successfully processed: {len(doc_list)} documents")
                
            except Exception as e:
                failed_urls.append(url)
                print(f"      ❌ Failed to process {url}: {e}")
                continue
        
        print(f"📊 URL List Summary:")
        print(f"   ✅ Successfully processed: {len(urls) - len(failed_urls)}/{len(urls)} URLs")
        print(f"   📄 Total documents: {len(all_documents)}")
        if failed_urls:
            print(f"   ❌ Failed URLs: {len(failed_urls)}")
            for url in failed_urls[:3]:  # Show first 3 failed URLs
                print(f"      - {url}")
            if len(failed_urls) > 3:
                print(f"      ... and {len(failed_urls) - 3} more")
        
        # Return documents in a format compatible with existing code
        class MockDocuments:
            def __init__(self, docs):
                self.docs = docs
            
            def to_dicts(self):
                return self.docs
            
            def __len__(self):
                return len(self.docs)
        
        return MockDocuments(all_documents)
    
    @staticmethod
    async def process_file(job_id: str, file_path: str, config: Dict[str, Any]):
        """Process a single file"""
        try:
            update_job_status(job_id, "processing")
            
            # Create loader and process
            loader_config = DocumentProcessingService.create_loader_config(config)
            loader = UniversalDataLoader(loader_config)
            documents = loader.load_file(file_path)
            
            # Save results
            output_file = get_result_file_path(job_id)
            loader.save_output(documents, output_file)
            
            # Update job status
            stats = documents.get_statistics()
            update_job_status(
                job_id, 
                "completed",
                documents_count=stats["document_count"],
                download_url=f"/download/{job_id}"
            )
            
        except Exception as e:
            update_job_status(job_id, "failed", error_message=str(e))
        
        finally:
            # Clean up uploaded file
            Path(file_path).unlink(missing_ok=True)
    
    @staticmethod
    async def process_url(job_id: str, url: str, config: Dict[str, Any]):
        """Process a single URL"""
        try:
            update_job_status(job_id, "processing")
            
            # Create loader and process
            loader_config = DocumentProcessingService.create_loader_config(config)
            loader = UniversalDataLoader(loader_config)
            documents = loader.load_url(url)
            
            # Save results
            output_file = get_result_file_path(job_id)
            loader.save_output(documents, output_file)
            
            # Update job status
            stats = documents.get_statistics()
            update_job_status(
                job_id,
                "completed", 
                documents_count=stats["document_count"],
                download_url=f"/download/{job_id}"
            )
            
        except Exception as e:
            update_job_status(job_id, "failed", error_message=str(e))
    
    @staticmethod
    async def process_batch(job_id: str, config: Dict[str, Any]):
        """Process multiple sources in batch - NEW IMPLEMENTATION"""
        try:
            print(f"🔧 DEBUG: NEW batch processing called for job {job_id}")
            update_job_status(job_id, "processing")
            
            # Process sources individually WITHOUT using BatchProcessor
            sources = config.get("sources", [])
            loader_config_data = config.get("loader_config", {})
            continue_on_error = config.get("continue_on_error", True)
            
            all_documents = []
            successful_sources = 0
            failed_sources = 0
            
            print(f"🔧 DEBUG: Processing {len(sources)} sources")
            
            for source_data in sources:
                try:
                    source_type = source_data.get("type")
                    source_path = source_data.get("path")
                    
                    print(f"🔧 DEBUG: Processing {source_type}: {source_path}")
                    
                    # Create a fresh loader for each source - use enable_chunking flag
                    loader_config_dict = {
                        "output_format": OutputFormat(loader_config_data.get("output_format", "documents")),
                        "include_metadata": loader_config_data.get("include_metadata", True),
                        "min_text_length": loader_config_data.get("min_text_length", 10),
                        "remove_headers_footers": loader_config_data.get("remove_headers_footers", True)
                    }
                    
                    # Only add chunking if enable_chunking=True
                    if loader_config_data.get("enable_chunking", False):
                        if not loader_config_data.get("chunking_strategy"):
                            raise ValueError("chunking_strategy is required when enable_chunking=True")
                        if not loader_config_data.get("max_chunk_size"):
                            raise ValueError("max_chunk_size is required when enable_chunking=True")
                            
                        loader_config_dict["chunking_strategy"] = ChunkingStrategy(loader_config_data["chunking_strategy"])
                        loader_config_dict["max_chunk_size"] = loader_config_data["max_chunk_size"]
                        
                        if loader_config_data.get("chunk_overlap") is not None:
                            loader_config_dict["chunk_overlap"] = loader_config_data["chunk_overlap"]
                    
                    loader_config = LoaderConfig(**loader_config_dict)
                    
                    loader = UniversalDataLoader(loader_config)
                    
                    # Process source individually
                    if source_type == "url":
                        documents = loader.load_url(source_path)
                    elif source_type == "file":
                        documents = loader.load_file(source_path)
                    elif source_type == "directory":
                        recursive = source_data.get("recursive", True)
                        documents = loader.load_directory(source_path, recursive=recursive)
                    elif source_type == "url_list":
                        # Process multiple URLs from a text file
                        documents = DocumentProcessingService._process_url_list(loader, source_path, source_data)
                    else:
                        raise ValueError(f"Unknown source type: {source_type}")
                    
                    # Convert to standard format
                    if hasattr(documents, 'to_dicts'):
                        doc_list = documents.to_dicts()
                    elif isinstance(documents, list):
                        doc_list = documents
                    else:
                        doc_list = [documents] if documents else []
                    
                    # Add batch metadata
                    for doc in doc_list:
                        if isinstance(doc, dict):
                            doc['metadata'] = doc.get('metadata', {})
                            doc['metadata']['source_path'] = source_path
                            doc['metadata']['source_type'] = source_type
                            doc['metadata']['batch_id'] = job_id
                    
                    all_documents.extend(doc_list)
                    successful_sources += 1
                    print(f"🔧 DEBUG: Successfully processed {source_path}: {len(doc_list)} documents")
                    
                except Exception as e:
                    failed_sources += 1
                    print(f"🔧 ERROR: Failed to process {source_data}: {e}")
                    if not continue_on_error:
                        raise
            
            print(f"🔧 DEBUG: Total documents collected: {len(all_documents)}")
            
            # Save documents directly as JSON array
            output_file = get_result_file_path(job_id)
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(all_documents, f, indent=2, ensure_ascii=False)
            
            print(f"🔧 DEBUG: Saved results to {output_file}")
            
            # Update job status
            update_job_status(
                job_id,
                "completed",
                documents_count=len(all_documents),
                successful_sources=successful_sources,
                failed_sources=failed_sources,
                download_url=f"/download/{job_id}"
            )
            
            print(f"🔧 DEBUG: Job {job_id} completed successfully")
            
        except Exception as e:
            print(f"🔧 ERROR: Batch processing failed: {e}")
            import traceback
            traceback.print_exc()
            update_job_status(job_id, "failed", error_message=str(e))