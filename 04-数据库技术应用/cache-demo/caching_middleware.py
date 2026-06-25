"""
FastAPI缓存中间件 - Day 4 数据库技术应用
自动为API响应添加Redis缓存层
"""

import time
import json
import hashlib
from typing import Optional, Callable, Any
from functools import wraps

from fastapi import Request, Response
from fastapi.routing import APIRoute
from starlette.middleware.base import BaseHTTPMiddleware

from redis_cache import RedisCache


class CacheMiddleware(BaseHTTPMiddleware):
    """
    Redis缓存中间件
    
    自动缓存GET请求的响应，支持：
    - 基于URL+查询参数的缓存键生成
    - 可配置的TTL（过期时间）
    - 指定路径排除/包含规则
    """
    
    def __init__(
        self,
        app,
        cache: RedisCache,
        cache_ttl: int = 300,
        exclude_paths: list = None,
        include_methods: list = None,
        key_prefix: str = "api_cache"
    ):
        """
        初始化缓存中间件
        
        Args:
            app: FastAPI应用实例
            cache: RedisCache实例
            cache_ttl: 默认缓存时间（秒）
            exclude_paths: 排除的路径列表（不缓存）
            include_methods: 包含的HTTP方法（默认只缓存GET）
            key_prefix: 缓存键前缀
        """
        super().__init__(app)
        
        self.cache = cache
        self.cache_ttl = cache_ttl
        self.exclude_paths = exclude_paths or ["/docs", "/redoc", "/openapi.json"]
        self.include_methods = include_methods or ["GET"]
        self.key_prefix = key_prefix
        
        # 统计信息
        self.stats = {
            'hits': 0,
            'misses': 0,
            'total_requests': 0
        }
    
    async def dispatch(self, request: Request, call_next) -> Response:
        """中间件处理逻辑"""
        
        # 只缓存指定的方法
        if request.method not in self.include_methods:
            return await call_next(request)
        
        # 排除指定路径
        path = request.url.path
        if any(path.startswith(exclude) for exclude in self.exclude_paths):
            return await call_next(request)
        
        # 生成缓存键
        cache_key = self._generate_cache_key(request)
        
        self.stats['total_requests'] += 1
        
        # 尝试从缓存获取
        cached_response = self.cache.get(cache_key)
        
        if cached_response is not None:
            self.stats['hits'] += 1
            
            print(f"🎯 缓存命中 [{request.method} {path}]")
            
            # 构建响应对象
            response = Response(
                content=cached_response['body'],
                status_code=cached_response['status'],
                media_type=cached_response.get('media_type', 'application/json'),
                headers=cached_response.get('headers', {})
            )
            
            response.headers["X-Cache"] = "HIT"
            return response
        
        # 缓存未命中，执行请求
        self.stats['misses'] += 1
        print(f"❌ 缓存未命中 [{request.method} {path}]")
        
        start_time = time.time()
        response = await call_next(request)
        process_time = (time.time() - start_time) * 1000
        
        # 缓存成功的响应（仅2xx状态码）
        if 200 <= response.status_code < 300:
            body = b""
            async for chunk in response.body_iterator:
                body += chunk
            
            cache_data = {
                'body': body.decode('utf-8') if isinstance(body, bytes) else str(body),
                'status': response.status_code,
                'media_type': response.media_type,
                'headers': dict(response.headers),
                'process_time_ms': round(process_time, 2)
            }
            
            # 存入缓存
            self.cache.set(cache_key, cache_data, ttl=self.cache_ttl)
            
            # 重新构建响应（因为已经消费了body）
            response = Response(
                content=cache_data['body'],
                status_code=response.status_code,
                media_type=response.media_type,
                headers={**response.headers, "X-Cache": "MISS"}
            )
        
        return response
    
    def _generate_cache_key(self, request: Request) -> str:
        """
        生成唯一的缓存键
        
        格式: {prefix}:{method}:{path}:{query_hash}
        """
        method = request.method
        path = request.url.path
        query_string = str(request.query_params)
        
        # 对查询参数进行哈希，避免键过长
        query_hash = hashlib.md5(query_string.encode()).hexdigest()[:8]
        
        cache_key = f"{self.key_prefix}:{method}:{path}:{query_hash}"
        
        return cache_key
    
    def get_stats(self) -> dict:
        """获取缓存统计"""
        total = self.stats['total_requests']
        hits = self.stats['hits']
        
        hit_rate = (hits / total * 100) if total > 0 else 0
        
        return {
            **self.stats,
            'hit_rate': f"{hit_rate:.2f}%"
        }
    
    def clear_stats(self):
        """重置统计"""
        self.stats = {'hits': 0, 'misses': 0, 'total_requests': 0}


def cached(
    ttl: int = 300,
    key_prefix: str = "func_cache",
    cache: Optional[RedisCache] = None
):
    """
    函数级缓存装饰器
    
    Usage:
        @cached(ttl=600)
        def get_expensive_data(param1, param2):
            # 耗时操作
            return result
    """
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            _cache = cache or create_redis_cache()
            
            # 生成函数调用签名作为缓存键
            func_signature = f"{func.__module__}.{func.__name__}"
            args_str = str(args) + str(kwargs)
            args_hash = hashlib.md5(args_str.encode()).hexdigest()
            
            cache_key = f"{key_prefix}:{func_signature}:{args_hash}"
            
            # 尝试从缓存获取
            result = _cache.get(cache_key)
            
            if result is not None:
                print(f"✅ 函数缓存命中: {func.__name__}")
                return result
            
            # 执行函数
            print(f"⏳ 执行函数并缓存: {func.__name__}")
            result = func(*args, **kwargs)
            
            # 存入缓存
            _cache.set(cache_key, result, ttl=ttl)
            
            return result
        
        return wrapper
    
    return decorator


# ===== 使用示例 =====

if __name__ == "__main__":
    print("""
╔════════════════════════════════════════╗
║     🚀 FastAPI 缓存中间件演示           ║
║     Day 4 数据库技术应用                 ║
╚════════════════════════════════════════╝
    """)
    
    try:
        from redis_cache import create_redis_cache
        
        # 创建缓存实例
        cache = create_redis_cache()
        
        if cache.ping():
            print("✅ Redis连接成功\n")
            
            # 测试函数级缓存装饰器
            @cached(ttl=60, cache=cache)
            def expensive_computation(n: int) -> int:
                """模拟耗时计算"""
                print(f"  ⏳ 正在计算 fib({n})...")
                time.sleep(1)  # 模拟耗时
                
                if n <= 1:
                    return n
                a, b = 0, 1
                for _ in range(2, n + 1):
                    a, b = b, a + b
                return b
            
            # 第一次调用（会执行）
            print("第1次调用:")
            start = time.time()
            result1 = expensive_computation(30)
            elapsed1 = time.time() - start
            print(f"  结果: {result1}, 耗时: {elapsed1:.3f}s\n")
            
            # 第二次调用（应该命中缓存）
            print("第2次调用（应命中缓存）:")
            start = time.time()
            result2 = expensive_computation(30)
            elapsed2 = time.time() - start
            print(f"  结果: {result2}, 耗时: {elapsed2:.3f}s\n")
            
            speedup = elapsed1 / elapsed2 if elapsed2 > 0 else float('inf')
            print(f"⚡ 加速比: {speedup:.1f}倍 ✅\n")
            
            # 清理测试数据
            cache.clear_all('func_cache:*')
            
            print("✅ 缓存装饰器演示完成！")
        
        else:
            print("❌ Redis连接失败")
            
    except ImportError as e:
        print(f"❌ 缺少依赖: {e}")
