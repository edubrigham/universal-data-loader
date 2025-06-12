#!/usr/bin/env python3
"""
Universal Data Loader Connector
Connects to the v1.1 REST API.

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

API_VERSION = "v1"

class UniversalLoaderConnector:
    """A Python client for the Universal Data Loader microservice."""
    
    def __init__(self, base_url: str = "http://localhost:8000", api_key: Optional[str] = None):
        self.base_url = base_url.rstrip('/')
        self.api_root = f"{self.base_url}/api/{API_VERSION}"
        self.session = requests.Session()
        
        # If an API key is provided, set it in the session headers.
        # This can also be sourced from an environment variable for convenience.
        key_to_use = api_key or os.getenv("ULOADER_API_KEY")
        if key_to_use:
            self.session.headers.update({"x-api-key": key_to_use})
            
        self.logger = self._setup_logging()
        self._verify_connection()
    
    def _get_endpoint(self, path: str) -> str:
        """Constructs the full API endpoint URL."""
        return f"{self.api_root}{path}"

    def get_documents_from_config(self, config_path: str, **kwargs) -> List[Dict[str, Any]]:
        """Processes all sources from a JSON config file."""
        config_file = Path(config_path)
        if not config_file.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_file}")
            
        with open(config_file, 'r') as f:
            config = json.load(f)
            
        self.logger.info(f"Processing {len(config.get('sources', []))} sources from '{config_file.name}'...")
        
        payload = {
            "sources": config.get("sources", []),
            "loader_config": config.get("processing", {}), # Maps user-friendly 'processing' to 'loader_config'
            **config.get("batch_options", {}),
            **kwargs
        }
        
        endpoint = self._get_endpoint("/jobs/batch")
        response = self.session.post(endpoint, json=payload)
        
        if response.status_code != 202:
            raise requests.HTTPError(f"Failed to create batch job: {response.text}")
            
        job_id = response.json()["job_id"]
        self.logger.info(f"Batch job '{job_id}' created.")
        
        return self._wait_for_job_completion(job_id)

    def process_url(self, url: str, config: Optional[Dict] = None, **kwargs) -> List[Dict[str, Any]]:
        """Processes a single URL."""
        payload = {"url": url, **(config or {}), **kwargs}
        endpoint = self._get_endpoint("/jobs/url")
        response = self.session.post(endpoint, json=payload)
        
        if response.status_code != 202:
            raise requests.HTTPError(f"Failed to create URL job: {response.text}")
            
        job_id = response.json()["job_id"]
        return self._wait_for_job_completion(job_id)

    def process_file(self, file_path: str, config: Optional[Dict] = None, **kwargs) -> List[Dict[str, Any]]:
        """Uploads and processes a single file."""
        if not Path(file_path).exists():
            raise FileNotFoundError(f"File not found: {file_path}")
            
        with open(file_path, 'rb') as f:
            files = {'file': (Path(file_path).name, f, 'application/octet-stream')}
            data = {'config': json.dumps(config or {}), **kwargs}
            endpoint = self._get_endpoint("/jobs/file")
            response = self.session.post(endpoint, files=files, data=data)
        
        if response.status_code != 202:
            raise requests.HTTPError(f"Failed to create file job: {response.text}")
            
        job_id = response.json()["job_id"]
        return self._wait_for_job_completion(job_id)

    def _wait_for_job_completion(self, job_id: str, timeout: int = 300) -> List[Dict[str, Any]]:
        """Polls for job completion and returns the final documents."""
        start_time = time.time()
        self.logger.info(f"Waiting for job '{job_id}' to complete...")
        
        while time.time() - start_time < timeout:
            result_endpoint = self._get_endpoint(f"/jobs/{job_id}/result")
            response = self.session.get(result_endpoint)
            
            if response.status_code == 200:
                self.logger.info(f"Job '{job_id}' completed successfully.")
                data = response.json()
                # Assuming the result is in the format {"documents": [...]}
                return data.get("documents", [])
            
            elif response.status_code == 202:
                # Job is still processing, wait and continue
                time.sleep(3)
                continue
            
            else:
                # Handle other statuses (404, 500, etc.) as errors
                response.raise_for_status()
        
        raise TimeoutError(f"Job '{job_id}' timed out after {timeout} seconds.")

    def health_check(self, **kwargs) -> Dict[str, Any]:
        """Checks the health of the microservice."""
        response = self.session.get(f"{self.base_url}/health")
        response.raise_for_status()
        return response.json()

    def _verify_connection(self):
        """Verifies connection to the microservice."""
        try:
            health = self.health_check()
            if health.get("status") == "healthy":
                self.logger.info(f"✅ Connected to Universal Data Loader at {self.base_url}")
            else:
                raise ConnectionError(f"Service not healthy: {health}")
        except requests.RequestException as e:
            raise ConnectionError(f"❌ Cannot connect to Universal Data Loader at {self.base_url}: {e}")

    @staticmethod
    def _setup_logging() -> logging.Logger:
        logger = logging.getLogger("UniversalLoaderClient")
        logger.setLevel(logging.INFO)
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        return logger


# --- Global Instance and Helper Functions ---
_connector_instance = None

def _get_connector(**kwargs) -> UniversalLoaderConnector:
    """Initializes and returns a global connector instance."""
    global _connector_instance
    if _connector_instance is None:
        # Pass kwargs to allow for flexible initialization (e.g., setting api_key)
        base_url = os.getenv("UNIVERSAL_LOADER_URL", "http://localhost:8000")
        _connector_instance = UniversalLoaderConnector(base_url=base_url, **kwargs)
    return _connector_instance

def get_documents_from_config(config_path: str, **kwargs) -> List[Dict[str, Any]]:
    """Primary function to get documents based on a config file."""
    return _get_connector(**kwargs).get_documents_from_config(config_path)

def process_url(url: str, config: Optional[Dict] = None, **kwargs) -> List[Dict[str, Any]]:
    """Helper function to process a single URL."""
    return _get_connector(**kwargs).process_url(url, config)

def process_file(file_path: str, config: Optional[Dict] = None, **kwargs) -> List[Dict[str, Any]]:
    """Helper function to process a single file."""
    return _get_connector(**kwargs).process_file(file_path, config)

def health_check(**kwargs) -> Dict[str, Any]:
    """Helper function to check microservice health."""
    return _get_connector(**kwargs).health_check()


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
        documents = get_documents_from_config("documents")
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