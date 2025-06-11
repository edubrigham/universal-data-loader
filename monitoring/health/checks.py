"""
Health Check System
Comprehensive health monitoring for the microservice
"""

import os
import psutil
from pathlib import Path
from typing import Dict, Any
from datetime import datetime

from app.services.job_service import get_active_jobs_count
from config.settings import settings


class HealthChecker:
    """Health check system for monitoring service status"""
    
    @staticmethod
    def check_disk_space() -> Dict[str, Any]:
        """Check available disk space"""
        try:
            upload_usage = psutil.disk_usage(settings.UPLOAD_DIR)
            output_usage = psutil.disk_usage(settings.OUTPUT_DIR)
            
            return {
                "status": "healthy",
                "upload_dir": {
                    "path": str(settings.UPLOAD_DIR),
                    "free_gb": round(upload_usage.free / (1024**3), 2),
                    "total_gb": round(upload_usage.total / (1024**3), 2),
                    "used_percent": round((upload_usage.used / upload_usage.total) * 100, 2)
                },
                "output_dir": {
                    "path": str(settings.OUTPUT_DIR),
                    "free_gb": round(output_usage.free / (1024**3), 2),
                    "total_gb": round(output_usage.total / (1024**3), 2),
                    "used_percent": round((output_usage.used / output_usage.total) * 100, 2)
                }
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }
    
    @staticmethod
    def check_memory() -> Dict[str, Any]:
        """Check memory usage"""
        try:
            memory = psutil.virtual_memory()
            return {
                "status": "healthy",
                "total_gb": round(memory.total / (1024**3), 2),
                "available_gb": round(memory.available / (1024**3), 2),
                "used_percent": memory.percent,
                "free_percent": round(100 - memory.percent, 2)
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }
    
    @staticmethod
    def check_cpu() -> Dict[str, Any]:
        """Check CPU usage"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            
            return {
                "status": "healthy",
                "usage_percent": cpu_percent,
                "core_count": cpu_count,
                "load_average": os.getloadavg() if hasattr(os, 'getloadavg') else None
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }
    
    @staticmethod
    def check_jobs() -> Dict[str, Any]:
        """Check job processing status"""
        try:
            active_jobs = get_active_jobs_count()
            return {
                "status": "healthy",
                "active_jobs": active_jobs,
                "max_workers": settings.MAX_WORKERS,
                "capacity_used_percent": round((active_jobs / settings.MAX_WORKERS) * 100, 2) if settings.MAX_WORKERS > 0 else 0
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }
    
    @classmethod
    def comprehensive_check(cls) -> Dict[str, Any]:
        """Perform comprehensive health check"""
        checks = {
            "timestamp": datetime.now().isoformat(),
            "service": "Universal Data Loader",
            "version": "1.0.0",
            "environment": settings.ENVIRONMENT,
            "disk": cls.check_disk_space(),
            "memory": cls.check_memory(),
            "cpu": cls.check_cpu(),
            "jobs": cls.check_jobs()
        }
        
        # Determine overall health
        unhealthy_checks = [k for k, v in checks.items() 
                           if isinstance(v, dict) and v.get("status") == "unhealthy"]
        
        checks["overall_status"] = "unhealthy" if unhealthy_checks else "healthy"
        checks["unhealthy_checks"] = unhealthy_checks
        
        return checks