# -*- coding: utf-8 -*-
"""
Job3.0 求职系统 - 缓存服务
"""

import json
import hashlib
from typing import Optional, Any
from functools import wraps
import time


class SimpleCache:
    """简单的内存缓存实现（无需Redis）"""
    
    def __init__(self, maxsize: int = 100, ttl: int = 3600):
        self._cache = {}
        self._timestamps = {}
        self.maxsize = maxsize
        self.ttl = ttl  # 秒
    
    def _is_expired(self, key: str) -> bool:
        if key not in self._timestamps:
            return True
        return time.time() - self._timestamps[key] > self.ttl
    
    def _generate_key(self, *args, **kwargs) -> str:
        key_data = json.dumps({"args": args, "kwargs": kwargs}, sort_keys=True)
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def get(self, key: str) -> Optional[Any]:
        if key in self._cache and not self._is_expired(key):
            return self._cache[key]
        return None
    
    def set(self, key: str, value: Any) -> None:
        # 简单的LRU：如果缓存满，删除最老的
        if len(self._cache) >= self.maxsize and key not in self._cache:
            oldest_key = min(self._timestamps.keys(), key=self._timestamps.get)
            del self._cache[oldest_key]
            del self._timestamps[oldest_key]
        
        self._cache[key] = value
        self._timestamps[key] = time.time()
    
    def delete(self, key: str) -> None:
        if key in self._cache:
            del self._cache[key]
        if key in self._timestamps:
            del self._timestamps[key]
    
    def clear(self) -> None:
        self._cache.clear()
        self._timestamps.clear()
    
    def cached(self, prefix: str = "", ttl: int = None):
        """装饰器：为函数添加缓存"""
        if ttl:
            original_ttl = self.ttl
            self.ttl = ttl
        
        def decorator(func):
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                cache_key = f"{prefix}:{func.__name__}:{self._generate_key(*args, **kwargs)}"
                
                # 尝试从缓存获取
                result = self.get(cache_key)
                if result is not None:
                    return result
                
                # 执行函数并缓存结果
                result = await func(*args, **kwargs)
                self.set(cache_key, result)
                return result
            
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                cache_key = f"{prefix}:{func.__name__}:{self._generate_key(*args, **kwargs)}"
                
                result = self.get(cache_key)
                if result is not None:
                    return result
                
                result = func(*args, **kwargs)
                self.set(cache_key, result)
                return result
            
            if hasattr(func, "__wrapped__") and hasattr(func, "__await__"):
                return async_wrapper
            return sync_wrapper
        
        if ttl:
            self.ttl = original_ttl
        
        return decorator


# 全局缓存实例
cache = SimpleCache(maxsize=200, ttl=1800)  # 30分钟TTL


def get_cache_key(*args) -> str:
    """生成缓存键"""
    return hashlib.md5(str(args).encode()).hexdigest()


def cached_result(prefix: str, ttl: int = 3600):
    """缓存装饰器工厂"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache_key = f"{prefix}:{func.__name__}:{get_cache_key(args, kwargs)}"
            
            # 尝试获取缓存
            cached = cache.get(cache_key)
            if cached is not None:
                return cached
            
            # 执行函数
            result = await func(*args, **kwargs) if hasattr(func, "__await__") else func(*args, **kwargs)
            
            # 存储缓存
            cache.set(cache_key, result)
            return result
        
        return wrapper
    return decorator
