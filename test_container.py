#!/usr/bin/env python3
"""
Container Testing Script for Universal Data Loader
Tests the containerized API endpoints
"""

import requests
import time
import json
import sys
from typing import Dict, Any

class ContainerTester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        
    def test_health_check(self) -> bool:
        """Test health endpoint"""
        print("🏥 Testing health check...")
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Health check passed: {data['status']}")
                return True
            else:
                print(f"❌ Health check failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Health check error: {e}")
            return False
    
    def test_url_processing(self) -> bool:
        """Test URL processing endpoint"""
        print("🌐 Testing URL processing...")
        try:
            response = self.session.post(
                f"{self.base_url}/process/url",
                json={
                    "url": "https://httpbin.org/json",
                    "output_format": "documents"
                },
                timeout=10
            )
            
            if response.status_code == 200:
                job_data = response.json()
                job_id = job_data["job_id"]
                print(f"✅ URL processing job created: {job_id}")
                
                # Wait for completion
                result = self._wait_for_job(job_id, timeout=60)
                if result:
                    print("✅ URL processing completed successfully")
                    return True
                else:
                    print("❌ URL processing failed or timed out")
                    return False
            else:
                print(f"❌ URL processing request failed: {response.status_code}")
                print(response.text)
                return False
                
        except Exception as e:
            print(f"❌ URL processing error: {e}")
            return False
    
    def test_batch_processing(self) -> bool:
        """Test batch processing endpoint"""
        print("📦 Testing batch processing...")
        try:
            response = self.session.post(
                f"{self.base_url}/process/batch",
                json={
                    "sources": [
                        {"type": "url", "path": "https://httpbin.org/json"},
                        {"type": "url", "path": "https://httpbin.org/user-agent"}
                    ],
                    "loader_config": {"output_format": "documents"},
                    "max_workers": 2
                },
                timeout=10
            )
            
            if response.status_code == 200:
                job_data = response.json()
                job_id = job_data["job_id"]
                print(f"✅ Batch processing job created: {job_id}")
                
                # Wait for completion
                result = self._wait_for_job(job_id, timeout=120)
                if result:
                    print("✅ Batch processing completed successfully")
                    return True
                else:
                    print("❌ Batch processing failed or timed out")
                    return False
            else:
                print(f"❌ Batch processing request failed: {response.status_code}")
                print(response.text)
                return False
                
        except Exception as e:
            print(f"❌ Batch processing error: {e}")
            return False
    
    def _wait_for_job(self, job_id: str, timeout: int = 60) -> bool:
        """Wait for job completion"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                response = self.session.get(f"{self.base_url}/jobs/{job_id}")
                if response.status_code == 200:
                    status_data = response.json()
                    status = status_data["status"]
                    
                    if status == "completed":
                        # Try to download result
                        download_response = self.session.get(f"{self.base_url}/download/{job_id}")
                        if download_response.status_code == 200:
                            result = download_response.json()
                            print(f"📄 Result contains {len(result)} documents")
                            return True
                        else:
                            print(f"❌ Failed to download result: {download_response.status_code}")
                            return False
                    
                    elif status == "failed":
                        error_msg = status_data.get("error_message", "Unknown error")
                        print(f"❌ Job failed: {error_msg}")
                        return False
                    
                    elif status in ["pending", "processing"]:
                        print(f"⏳ Job status: {status}")
                        time.sleep(2)
                        continue
                    
                else:
                    print(f"❌ Failed to get job status: {response.status_code}")
                    return False
                    
            except Exception as e:
                print(f"❌ Error checking job status: {e}")
                return False
        
        print(f"❌ Job timed out after {timeout} seconds")
        return False
    
    def test_api_documentation(self) -> bool:
        """Test API documentation endpoint"""
        print("📚 Testing API documentation...")
        try:
            response = self.session.get(f"{self.base_url}/docs", timeout=10)
            if response.status_code == 200:
                print("✅ API documentation accessible")
                return True
            else:
                print(f"❌ API documentation failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ API documentation error: {e}")
            return False
    
    def run_all_tests(self) -> bool:
        """Run all tests"""
        print("🧪 Universal Data Loader Container Tests")
        print("=" * 50)
        
        tests = [
            ("Health Check", self.test_health_check),
            ("API Documentation", self.test_api_documentation),
            ("URL Processing", self.test_url_processing),
            ("Batch Processing", self.test_batch_processing)
        ]
        
        results = []
        for test_name, test_func in tests:
            print(f"\n🔸 {test_name}")
            result = test_func()
            results.append(result)
            time.sleep(1)  # Brief pause between tests
        
        print("\n" + "=" * 50)
        print("📊 Test Results Summary")
        print("=" * 50)
        
        for i, (test_name, _) in enumerate(tests):
            status = "✅ PASS" if results[i] else "❌ FAIL"
            print(f"{test_name}: {status}")
        
        passed = sum(results)
        total = len(results)
        print(f"\nOverall: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All tests passed! Container is working correctly.")
            return True
        else:
            print("⚠️ Some tests failed. Check the logs above for details.")
            return False


def main():
    """Main test function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test Universal Data Loader container")
    parser.add_argument("--url", default="http://localhost:8000", 
                       help="Base URL for the service (default: http://localhost:8000)")
    parser.add_argument("--wait", type=int, default=30,
                       help="Wait time for service to start (default: 30 seconds)")
    
    args = parser.parse_args()
    
    print(f"🚀 Testing Universal Data Loader at: {args.url}")
    
    # Wait for service to be ready
    if args.wait > 0:
        print(f"⏳ Waiting {args.wait} seconds for service to start...")
        time.sleep(args.wait)
    
    # Run tests
    tester = ContainerTester(args.url)
    success = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()