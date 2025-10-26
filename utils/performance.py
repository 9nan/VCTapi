import time
import logging
from functools import wraps
from typing import Callable, Any
import asyncio

logger = logging.getLogger(__name__)

class PerformanceMonitor:
    """Performance monitoring utilities"""
    
    @staticmethod
    def time_function(func: Callable) -> Callable:
        """Decorator to time function execution"""
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                execution_time = time.time() - start_time
                logger.info(f"{func.__name__} executed in {execution_time:.3f}s")
                return result
            except Exception as e:
                execution_time = time.time() - start_time
                logger.error(f"{func.__name__} failed after {execution_time:.3f}s: {e}")
                raise
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                logger.info(f"{func.__name__} executed in {execution_time:.3f}s")
                return result
            except Exception as e:
                execution_time = time.time() - start_time
                logger.error(f"{func.__name__} failed after {execution_time:.3f}s: {e}")
                raise
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    @staticmethod
    def monitor_memory():
        """Monitor memory usage"""
        try:
            import psutil
            process = psutil.Process()
            memory_info = process.memory_info()
            logger.info(f"Memory usage: {memory_info.rss / 1024 / 1024:.2f} MB")
        except ImportError:
            logger.warning("psutil not available for memory monitoring")
    
    @staticmethod
    def log_performance_stats(stats: dict):
        """Log performance statistics"""
        logger.info("Performance Statistics:")
        for key, value in stats.items():
            logger.info(f"  {key}: {value}")

# Global performance tracker
performance_stats = {
    "total_requests": 0,
    "successful_requests": 0,
    "failed_requests": 0,
    "average_response_time": 0,
    "cache_hits": 0,
    "cache_misses": 0
}

def track_request(func: Callable) -> Callable:
    """Decorator to track request statistics"""
    @wraps(func)
    async def async_wrapper(*args, **kwargs):
        global performance_stats
        start_time = time.time()
        performance_stats["total_requests"] += 1
        
        try:
            result = await func(*args, **kwargs)
            performance_stats["successful_requests"] += 1
            execution_time = time.time() - start_time
            
            # Update average response time
            total_successful = performance_stats["successful_requests"]
            current_avg = performance_stats["average_response_time"]
            performance_stats["average_response_time"] = (
                (current_avg * (total_successful - 1) + execution_time) / total_successful
            )
            
            return result
        except Exception as e:
            performance_stats["failed_requests"] += 1
            logger.error(f"Request failed: {e}")
            raise
    
    @wraps(func)
    def sync_wrapper(*args, **kwargs):
        global performance_stats
        start_time = time.time()
        performance_stats["total_requests"] += 1
        
        try:
            result = func(*args, **kwargs)
            performance_stats["successful_requests"] += 1
            execution_time = time.time() - start_time
            
            # Update average response time
            total_successful = performance_stats["successful_requests"]
            current_avg = performance_stats["average_response_time"]
            performance_stats["average_response_time"] = (
                (current_avg * (total_successful - 1) + execution_time) / total_successful
            )
            
            return result
        except Exception as e:
            performance_stats["failed_requests"] += 1
            logger.error(f"Request failed: {e}")
            raise
    
    if asyncio.iscoroutinefunction(func):
        return async_wrapper
    else:
        return sync_wrapper

def get_performance_stats() -> dict:
    """Get current performance statistics"""
    return performance_stats.copy()

def reset_performance_stats():
    """Reset performance statistics"""
    global performance_stats
    performance_stats = {
        "total_requests": 0,
        "successful_requests": 0,
        "failed_requests": 0,
        "average_response_time": 0,
        "cache_hits": 0,
        "cache_misses": 0
    }
