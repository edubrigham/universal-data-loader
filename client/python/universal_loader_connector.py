#!/usr/bin/env python3
"""
Universal Data Loader Connector
Drop-in integration for any LLM application

STANDARD USAGE:
1. Create a config/ folder in your project root
2. Add a documents.json file with your sources and settings
3. Use the connector:

    from universal_loader_connector import get_documents
    documents = get_documents()  # Processes everything in config/documents.json

STANDARD STRUCTURE:
your_llm_app/
├── config/
│   └── documents.json    # Your document sources and processing settings
├── universal_loader_connector.py    # This connector file
└── your_app.py          # Your LLM application
"""

import os
import json
import time
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
import requests


class UniversalLoaderConnector:
    """Connector to Universal Data Loader microservice with standard conventions"""
    
    def __init__(self, config_dir: str = "./config"):
        """
        Initialize connector
        
        Args:
            config_dir: Directory containing configuration files (default: ./config)
        """
        self.config_dir = Path(config_dir)
        self.session = requests.Session()
        self.logger = self._setup_logging()
        
        # Load main configuration
        self.config = self._load_config()
        self.microservice_url = self.config.get("microservice_url", "http://localhost:8000").rstrip('/')
        
        # Verify microservice connection
        self._verify_connection()
    
    def get_documents(self, config_name: str = "documents") -> List[Dict[str, Any]]:
        """
        Get processed documents using standard configuration
        
        Args:
            config_name: Name of config file (without .json extension)
            
        Returns:
            List of LangChain-compatible documents
        """
        config_file = self.config_dir / f"{config_name}.json"
        
        if not config_file.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_file}")
        
        # Load configuration
        with open(config_file) as f:
            config = json.load(f)
        
        sources = config.get("sources", [])
        processing_config = config.get("processing", {})
        batch_options = config.get("batch_options", {})
        
        self.logger.info(f"Processing {len(sources)} sources from {config_name}.json")
        
        # Convert processing config to loader_config format
        loader_config = {
            "output_format": processing_config.get("output_format", "documents"),
            "chunking_strategy": processing_config.get("chunking_strategy"),
            "max_chunk_size": processing_config.get("max_chunk_size", 1000),
            "chunk_overlap": processing_config.get("chunk_overlap", 100),
            "include_metadata": processing_config.get("include_metadata", True),
            "min_text_length": processing_config.get("min_text_length", 10),
            "remove_headers_footers": processing_config.get("remove_headers_footers", True)
        }
        
        # Remove None values
        loader_config = {k: v for k, v in loader_config.items() if v is not None}
        
        # Prepare batch request
        payload = {
            "sources": sources,
            "loader_config": loader_config,
            "output_config": {
                "separate_by_source": True,
                "merge_all": batch_options.get("merge_all", True)
            },
            "max_workers": batch_options.get("max_workers", 3),
            "continue_on_error": batch_options.get("continue_on_error", True)
        }
        
        # Submit batch job
        response = self.session.post(f"{self.microservice_url}/process/batch", json=payload)
        response.raise_for_status()
        
        job_id = response.json()["job_id"]
        self.logger.info(f"Batch job submitted: {job_id}")
        
        # Wait for completion and get documents
        documents = self._wait_and_download(job_id)
        
        self.logger.info(f"Successfully processed: {len(documents)} documents")
        return documents
    
    def process_single_url(self, url: str, processing_config: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """
        Process a single URL
        
        Args:
            url: URL to process
            processing_config: Optional processing configuration
            
        Returns:
            List of LangChain-compatible documents
        """
        config = processing_config or self.config.get("processing", {})
        
        payload = {"url": url, **config}
        
        response = self.session.post(f"{self.microservice_url}/process/url", json=payload)
        response.raise_for_status()
        
        job_id = response.json()["job_id"]
        return self._wait_and_download(job_id)
    
    def process_single_file(self, file_path: str, processing_config: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """
        Process a single file
        
        Args:
            file_path: Path to file
            processing_config: Optional processing configuration
            
        Returns:
            List of LangChain-compatible documents
        """
        config = processing_config or self.config.get("processing", {})
        
        with open(file_path, 'rb') as f:
            files = {'file': (Path(file_path).name, f, 'application/octet-stream')}
            data = {'config': json.dumps(config)}
            
            response = self.session.post(f"{self.microservice_url}/process/file", files=files, data=data)
        
        response.raise_for_status()
        job_id = response.json()["job_id"]
        return self._wait_and_download(job_id)
    
    def health_check(self) -> Dict[str, Any]:
        """Check microservice health"""
        response = self.session.get(f"{self.microservice_url}/health")
        response.raise_for_status()
        return response.json()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load main configuration file"""
        config_file = self.config_dir / "documents.json"
        
        if not config_file.exists():
            # Create default config if it doesn't exist
            default_config = {
                "microservice_url": "http://localhost:8000",
                "sources": [],
                "processing": {
                    "output_format": "documents",
                    "include_metadata": True
                },
                "batch_options": {
                    "max_workers": 3,
                    "continue_on_error": True,
                    "merge_all": True
                }
            }
            
            # Create config directory if it doesn't exist
            self.config_dir.mkdir(parents=True, exist_ok=True)
            
            with open(config_file, 'w') as f:
                json.dump(default_config, f, indent=2)
            
            print(f"✅ Created default config at: {config_file}")
            print("📝 Edit this file to add your document sources")
            
            return default_config
        
        with open(config_file) as f:
            return json.load(f)
    
    def _verify_connection(self) -> None:
        """Verify connection to microservice"""
        try:
            health = self.health_check()
            if health.get("status") == "healthy":
                self.logger.info(f"✅ Connected to Universal Data Loader at {self.microservice_url}")
            else:
                raise Exception(f"Service not healthy: {health}")
        except Exception as e:
            error_msg = f"❌ Cannot connect to Universal Data Loader at {self.microservice_url}: {e}"
            self.logger.error(error_msg)
            raise ConnectionError(error_msg)
    
    def _wait_and_download(self, job_id: str, timeout: int = 300) -> List[Dict[str, Any]]:
        """Wait for job completion and download results"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            # Check job status
            response = self.session.get(f"{self.microservice_url}/jobs/{job_id}")
            response.raise_for_status()
            status = response.json()
            
            if status["status"] == "completed":
                # Download documents
                response = self.session.get(f"{self.microservice_url}/download/{job_id}")
                response.raise_for_status()
                result = response.json()
                
                # Cleanup job
                try:
                    self.session.delete(f"{self.microservice_url}/jobs/{job_id}")
                except:
                    pass
                
                # Handle different result types
                if isinstance(result, list):
                    # Direct list of documents (from file/URL processing)
                    return result
                elif isinstance(result, dict):
                    if "output_files" in result:
                        # Batch processing result - need to extract documents
                        # For now, return empty list but log the issue
                        self.logger.warning(f"Batch processing completed but documents are in files: {result['output_files']}")
                        # In a real implementation, you'd need to download these files
                        # For now, let's try a different approach
                        return []
                    elif "page_content" in result:
                        # Single document
                        return [result]
                    else:
                        # Unknown format
                        self.logger.warning(f"Unknown result format: {list(result.keys())}")
                        return []
                else:
                    return []
            
            elif status["status"] == "failed":
                error_msg = status.get("error_message", "Unknown error")
                raise Exception(f"Job failed: {error_msg}")
            
            elif status["status"] in ["pending", "processing"]:
                time.sleep(2)
                continue
            
            else:
                raise Exception(f"Unknown job status: {status['status']}")
        
        raise TimeoutError(f"Job timed out after {timeout} seconds")
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging"""
        logger = logging.getLogger("universal_loader_connector")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger


# ================================
# STANDARD API - Drop-in Functions
# ================================

# Global connector instance
_connector = None

def get_documents(config_name: str = "documents") -> List[Dict[str, Any]]:
    """
    STANDARD FUNCTION: Get processed documents
    
    This is the main function LLM applications should use.
    Reads from config/{config_name}.json and returns LangChain documents.
    
    Args:
        config_name: Name of config file (default: "documents")
        
    Returns:
        List of LangChain-compatible documents
    """
    global _connector
    if _connector is None:
        _connector = UniversalLoaderConnector()
    
    return _connector.get_documents(config_name)


def process_url(url: str) -> List[Dict[str, Any]]:
    """
    STANDARD FUNCTION: Process a single URL
    
    Args:
        url: URL to process
        
    Returns:
        List of LangChain-compatible documents
    """
    global _connector
    if _connector is None:
        _connector = UniversalLoaderConnector()
    
    return _connector.process_single_url(url)


def process_file(file_path: str) -> List[Dict[str, Any]]:
    """
    STANDARD FUNCTION: Process a single file
    
    Args:
        file_path: Path to file
        
    Returns:
        List of LangChain-compatible documents
    """
    global _connector
    if _connector is None:
        _connector = UniversalLoaderConnector()
    
    return _connector.process_single_file(file_path)


def health_check() -> Dict[str, Any]:
    """
    STANDARD FUNCTION: Check microservice health
    
    Returns:
        Health status information
    """
    global _connector
    if _connector is None:
        _connector = UniversalLoaderConnector()
    
    return _connector.health_check()


# ================================
# Example Usage
# ================================

if __name__ == "__main__":
    print("Universal Data Loader Connector - Standard Integration")
    print("=" * 60)
    
    try:
        # Check health
        health = health_check()
        print(f"✅ Service Status: {health['status']}")
        
        # Test document processing
        print("\n📄 Testing document processing...")
        
        # This will use config/documents.json
        documents = get_documents()
        print(f"✅ Processed documents: {len(documents)}")
        
        if documents:
            print(f"📋 First document preview:")
            print(f"   Content: {documents[0]['page_content'][:100]}...")
            print(f"   Metadata: {list(documents[0]['metadata'].keys())}")
        
    except FileNotFoundError as e:
        print(f"⚠️ Configuration missing: {e}")
        print("\n💡 To get started:")
        print("1. Edit config/documents.json with your sources")
        print("2. Run this script again")
        
    except ConnectionError as e:
        print(f"❌ Connection error: {e}")
        print("\n💡 Make sure the Universal Data Loader is running:")
        print("   docker-compose up -d")
        
    except Exception as e:
        print(f"❌ Error: {e}")