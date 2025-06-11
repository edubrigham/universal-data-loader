#!/usr/bin/env python3
"""
Universal Data Loader Client Library
Example integration for LLM applications
"""

import requests
import time
import json
from typing import List, Dict, Any, Optional, Union
from pathlib import Path


class UniversalDataLoaderClient:
    """
    Client library for Universal Data Loader microservice
    
    Example usage:
        client = UniversalDataLoaderClient("http://localhost:8000")
        documents = client.process_url("https://example.com/article")
        
        # Use with LangChain
        from langchain_chroma import Chroma
        vectorstore = Chroma.from_documents(documents)
    """
    
    def __init__(self, base_url: str = "http://localhost:8000", timeout: int = 300):
        """
        Initialize client
        
        Args:
            base_url: URL of the Universal Data Loader service
            timeout: Default timeout for processing jobs
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.session = requests.Session()
    
    def health_check(self) -> Dict[str, Any]:
        """Check service health"""
        response = self.session.get(f"{self.base_url}/health")
        response.raise_for_status()
        return response.json()
    
    def process_url(self, url: str, config: Optional[Dict[str, Any]] = None, 
                   wait: bool = True) -> Union[List[Dict], str]:
        """
        Process a URL and return LangChain-compatible documents
        
        Args:
            url: URL to process
            config: Processing configuration
            wait: If True, wait for completion and return documents
                 If False, return job_id for async processing
        
        Returns:
            List of LangChain Documents or job_id string
        """
        if config is None:
            config = {"output_format": "documents"}
        
        payload = {"url": url, **config}
        response = self.session.post(f"{self.base_url}/process/url", json=payload)
        response.raise_for_status()
        
        job_id = response.json()["job_id"]
        
        if wait:
            return self._wait_and_download(job_id)
        return job_id
    
    def process_file(self, file_path: Union[str, Path], 
                    config: Optional[Dict[str, Any]] = None,
                    wait: bool = True) -> Union[List[Dict], str]:
        """
        Process a file and return LangChain-compatible documents
        
        Args:
            file_path: Path to file to process
            config: Processing configuration
            wait: If True, wait for completion and return documents
        
        Returns:
            List of LangChain Documents or job_id string
        """
        if config is None:
            config = {"output_format": "documents"}
        
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        with open(file_path, 'rb') as f:
            files = {'file': (file_path.name, f, 'application/octet-stream')}
            data = {'config': json.dumps(config)}
            
            response = self.session.post(
                f"{self.base_url}/process/file", 
                files=files, 
                data=data
            )
        
        response.raise_for_status()
        job_id = response.json()["job_id"]
        
        if wait:
            return self._wait_and_download(job_id)
        return job_id
    
    def process_batch(self, sources: List[Dict[str, Any]], 
                     loader_config: Optional[Dict[str, Any]] = None,
                     output_config: Optional[Dict[str, Any]] = None,
                     max_workers: int = 3,
                     wait: bool = True) -> Union[Dict[str, Any], str]:
        """
        Process multiple sources in batch
        
        Args:
            sources: List of source configurations
            loader_config: Global processing configuration
            output_config: Output configuration
            max_workers: Number of parallel workers
            wait: If True, wait for completion and return results
        
        Returns:
            Batch processing results or job_id string
        """
        if loader_config is None:
            loader_config = {"output_format": "documents"}
        
        if output_config is None:
            output_config = {"separate_by_source": True, "merge_all": False}
        
        payload = {
            "sources": sources,
            "loader_config": loader_config,
            "output_config": output_config,
            "max_workers": max_workers
        }
        
        response = self.session.post(f"{self.base_url}/process/batch", json=payload)
        response.raise_for_status()
        
        job_id = response.json()["job_id"]
        
        if wait:
            return self._wait_and_download(job_id)
        return job_id
    
    def get_job_status(self, job_id: str) -> Dict[str, Any]:
        """Get job status"""
        response = self.session.get(f"{self.base_url}/jobs/{job_id}")
        response.raise_for_status()
        return response.json()
    
    def download_result(self, job_id: str) -> Union[List[Dict], Dict[str, Any]]:
        """Download job results"""
        response = self.session.get(f"{self.base_url}/download/{job_id}")
        response.raise_for_status()
        return response.json()
    
    def cleanup_job(self, job_id: str) -> None:
        """Clean up job files and data"""
        response = self.session.delete(f"{self.base_url}/jobs/{job_id}")
        response.raise_for_status()
    
    def _wait_and_download(self, job_id: str) -> Union[List[Dict], Dict[str, Any]]:
        """Wait for job completion and download results"""
        start_time = time.time()
        
        while time.time() - start_time < self.timeout:
            status = self.get_job_status(job_id)
            
            if status["status"] == "completed":
                result = self.download_result(job_id)
                # Auto-cleanup completed jobs
                try:
                    self.cleanup_job(job_id)
                except:
                    pass  # Cleanup is optional
                return result
            
            elif status["status"] == "failed":
                error_msg = status.get("error_message", "Unknown error")
                raise RuntimeError(f"Job {job_id} failed: {error_msg}")
            
            elif status["status"] in ["pending", "processing"]:
                time.sleep(2)
                continue
            
            else:
                raise RuntimeError(f"Unknown job status: {status['status']}")
        
        raise TimeoutError(f"Job {job_id} timed out after {self.timeout} seconds")


# Example integration patterns

class RAGKnowledgeBuilder:
    """Example: Building RAG knowledge base"""
    
    def __init__(self, data_loader_url: str = "http://localhost:8000"):
        self.client = UniversalDataLoaderClient(data_loader_url)
    
    def build_knowledge_base(self, sources: List[Dict[str, Any]]) -> List[Dict]:
        """
        Build knowledge base from various document sources
        
        Args:
            sources: List of sources in format:
                [{"type": "url", "path": "https://docs.company.com"},
                 {"type": "file", "path": "/data/manual.pdf"},
                 {"type": "directory", "path": "/data/policies/"}]
        
        Returns:
            List of LangChain-compatible documents
        """
        print(f"🔨 Building knowledge base from {len(sources)} sources...")
        
        # Process all sources in batch
        results = self.client.process_batch(
            sources=sources,
            loader_config={
                "output_format": "documents",
                "chunking_strategy": "by_title",
                "max_chunk_size": 800,
                "chunk_overlap": 100,
                "include_metadata": True
            },
            max_workers=3
        )
        
        # Extract documents from batch results
        all_documents = []
        if isinstance(results, dict) and "output_files" in results:
            # Download individual files
            for source_path, output_file in results["output_files"].items():
                if "merged" not in source_path:  # Skip merged file
                    # In real implementation, you'd download these files
                    # For this example, we'll simulate
                    print(f"📄 Processed {source_path}: {output_file}")
        
        print(f"✅ Knowledge base built with {len(all_documents)} documents")
        return all_documents


class DocumentProcessor:
    """Example: Real-time document processing"""
    
    def __init__(self, data_loader_url: str = "http://localhost:8000"):
        self.client = UniversalDataLoaderClient(data_loader_url)
    
    def process_uploaded_file(self, file_path: str) -> List[Dict]:
        """Process a newly uploaded file"""
        print(f"📁 Processing uploaded file: {file_path}")
        
        documents = self.client.process_file(
            file_path=file_path,
            config={
                "output_format": "documents",
                "include_metadata": True,
                "min_text_length": 50
            }
        )
        
        print(f"✅ Extracted {len(documents)} documents")
        return documents
    
    def process_web_content(self, url: str) -> List[Dict]:
        """Process web content for analysis"""
        print(f"🌐 Processing web content: {url}")
        
        documents = self.client.process_url(
            url=url,
            config={
                "output_format": "documents",
                "remove_headers_footers": True,
                "min_text_length": 100
            }
        )
        
        print(f"✅ Extracted {len(documents)} documents from web page")
        return documents


# Example usage demonstrations

def demo_basic_usage():
    """Demonstrate basic client usage"""
    print("🚀 Basic Usage Demo")
    print("=" * 50)
    
    # Initialize client
    client = UniversalDataLoaderClient("http://localhost:8000")
    
    # Check service health
    try:
        health = client.health_check()
        print(f"✅ Service is healthy: {health['status']}")
    except Exception as e:
        print(f"❌ Service health check failed: {e}")
        return
    
    # Process a URL
    try:
        print("\n🌐 Processing URL...")
        documents = client.process_url(
            "https://httpbin.org/json",
            config={"output_format": "documents", "include_metadata": True}
        )
        print(f"✅ URL processed: {len(documents)} documents")
        
        # Show first document
        if documents:
            doc = documents[0]
            print(f"📄 Sample document:")
            print(f"   Content: {doc['page_content'][:100]}...")
            print(f"   Metadata keys: {list(doc['metadata'].keys())}")
    
    except Exception as e:
        print(f"❌ URL processing failed: {e}")


def demo_batch_processing():
    """Demonstrate batch processing"""
    print("\n📦 Batch Processing Demo")
    print("=" * 50)
    
    client = UniversalDataLoaderClient("http://localhost:8000")
    
    sources = [
        {"type": "url", "path": "https://httpbin.org/json"},
        {"type": "url", "path": "https://httpbin.org/user-agent"}
    ]
    
    try:
        print(f"🔄 Processing {len(sources)} sources in batch...")
        results = client.process_batch(
            sources=sources,
            loader_config={"output_format": "documents"},
            max_workers=2
        )
        
        print(f"✅ Batch processing completed")
        print(f"📊 Results: {results.get('total_documents', 0)} total documents")
        
    except Exception as e:
        print(f"❌ Batch processing failed: {e}")


def demo_rag_integration():
    """Demonstrate RAG knowledge base building"""
    print("\n🧠 RAG Integration Demo")
    print("=" * 50)
    
    rag_builder = RAGKnowledgeBuilder("http://localhost:8000")
    
    sources = [
        {"type": "url", "path": "https://httpbin.org/json"},
        {"type": "url", "path": "https://en.wikipedia.org/wiki/Machine_learning"}
    ]
    
    try:
        documents = rag_builder.build_knowledge_base(sources)
        print(f"✅ RAG knowledge base ready with {len(documents)} documents")
        
    except Exception as e:
        print(f"❌ RAG integration failed: {e}")


if __name__ == "__main__":
    """Run all demos"""
    print("🎯 Universal Data Loader Client Examples")
    print("=" * 60)
    
    # Run demonstrations
    demo_basic_usage()
    demo_batch_processing() 
    demo_rag_integration()
    
    print("\n🎉 Demo completed!")
    print("\n💡 Integration tips:")
    print("• Use async processing for large batches")
    print("• Implement retry logic for production")
    print("• Monitor job status for long-running tasks")
    print("• Clean up completed jobs to save storage")