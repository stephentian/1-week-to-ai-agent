"""
Redis缓存封装类 - Day 4 数据库技术应用
提供完整的Redis操作接口和防护机制
"""

import json
import time
import random
import threading
from typing import Any, Optional, Dict, List
from datetime import timedelta

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False


class RedisCache:
    """Redis缓存管理器"""
    
    def __init__(
        self,
        host: str = 'localhost',
        port: int = 6379,
        db: int = 0,
        password: Optional[str] = None,
        socket_timeout: float = 5.0,
        max_connections: int = 10,
        decode_responses: bool = True
    ):
        """
        初始化Redis连接
        
        Args:
            host: Redis主机地址
            port: Redis端口
            db: 数据库编号（0-15）
            password: 密码
            socket_timeout: 连接超时时间（秒）
            max_connections: 连接池最大连接数
            decode_responses: 是否自动解码响应为字符串
        """
        if not REDIS_AVAILABLE:
            raise ImportError("请安装redis库: pip install redis")
        
        self.host = host
        self.port = port
        
        # 创建连接池
        self.pool = redis.ConnectionPool(
            host=host,
            port=port,
            db=db,
            password=password,
            socket_timeout=socket_timeout,
            max_connections=max_connections,
            decode_responses=decode_responses
        )
        
        # 获取客户端实例
        self._client = redis.Redis(connection_pool=self.pool)
        
        # 互斥锁字典（用于缓存击穿防护）
        self._locks: Dict[str, threading.Lock] = {}
        self._locks_lock = threading.Lock()
    
    @property
    def client(self) -> redis.Redis:
        """获取Redis客户端"""
        return self._client
    
    # ===== 基础操作 =====
    
    def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
        nx: bool = False,
        xx: bool = False
    ) -> bool:
        """
        设置缓存值
        
        Args:
            key: 键名
            value: 值（支持dict/list/str/int等）
            ttl: 过期时间（秒），None表示永不过期
            nx: 仅当键不存在时设置
            xx: 仅当键已存在时设置
            
        Returns:
            是否设置成功
        """
        try:
            # 序列化值
            serialized_value = self._serialize(value)
            
            if ttl is not None:
                return self.client.setex(key, ttl, serialized_value)
            else:
                return self.client.set(key, serialized_value, nx=nx, xx=xx)
                
        except Exception as e:
            print(f"❌ 设置缓存失败 [{key}]: {e}")
            return False
    
    def get(self, key: str) -> Any:
        """
        获取缓存值
        
        Args:
            key: 键名
            
        Returns:
            缓存值，不存在返回None
        """
        try:
            value = self.client.get(key)
            
            if value is not None:
                return self._deserialize(value)
            return None
            
        except Exception as e:
            print(f"❌ 获取缓存失败 [{key}]: {e}")
            return None
    
    def delete(self, *keys: str) -> int:
        """
        删除一个或多个键
        
        Args:
            *keys: 要删除的键名列表
            
        Returns:
            实际删除的键数量
        """
        if not keys:
            return 0
        
        try:
            return self.client.delete(*keys)
        except Exception as e:
            print(f"❌ 删除缓存失败: {e}")
            return 0
    
    def exists(self, key: str) -> bool:
        """检查键是否存在"""
        try:
            return bool(self.client.exists(key))
        except Exception:
            return False
    
    def expire(self, key: str, ttl: int) -> bool:
        """设置键的过期时间"""
        try:
            return self.client.expire(key, ttl)
        except Exception as e:
            print(f"❌ 设置过期时间失败: {e}")
            return False
    
    def ttl(self, key: str) -> int:
        """
        获取键的剩余过期时间（秒）
        
        Returns:
            -2: 键不存在
            -1: 永不过期
            >0: 剩余秒数
        """
        try:
            return self.client.ttl(key)
        except Exception:
            return -2
    
    # ===== 批量操作 =====
    
    def mget(self, keys: List[str]) -> List[Any]:
        """批量获取多个键的值"""
        if not keys:
            return []
        
        try:
            values = self.client.mget(keys)
            return [self._deserialize(v) if v else None for v in values]
        except Exception as e:
            print(f"❌ 批量获取失败: {e}")
            return [None] * len(keys)
    
    def mset(self, mapping: Dict[str, Any], ttl: Optional[int] = None) -> bool:
        """批量设置多个键值对"""
        if not mapping:
            return False
        
        try:
            serialized_mapping = {k: self._serialize(v) for k, v in mapping.items()}
            
            result = self.client.mset(serialized_mapping)
            
            # 如果设置了TTL，逐个设置过期时间
            if ttl and result:
                pipe = self.client.pipeline()
                for key in mapping.keys():
                    pipe.expire(key, ttl)
                pipe.execute()
            
            return result
            
        except Exception as e:
            print(f"❌ 批量设置失败: {e}")
            return False
    
    # ===== 高级功能 - 防护机制 =====
    
    def get_with_null_cache(
        self,
        key: str,
        load_func: callable,
        ttl: int = 1800,
        null_ttl: int = 60
    ) -> Any:
        """
        带空值缓存的获取方法（防止缓存穿透）
        
        当查询结果为空时，也会缓存一个特殊标记，避免频繁查数据库
        
        Args:
            key: 缓存键名
            load_func: 数据加载函数（从数据库查询）
            ttl: 正常数据的缓存时间（秒）
            null_ttl: 空值的缓存时间（秒，通常较短）
            
        Returns:
            查询结果，如果数据不存在返回None
        """
        # 1. 先查缓存
        cached = self.get(key)
        
        # 2. 检查是否是空值标记
        if cached is not None:
            if isinstance(cached, dict) and '__NULL_CACHE__' in cached:
                return None  # 返回空结果
            return cached
        
        # 3. 缓存未命中，加载数据
        data = load_func()
        
        if data is not None:
            # 正常数据，正常TTL
            self.set(key, data, ttl=ttl)
        else:
            # 空数据，短TTL防止穿透
            self.set(key, {'__NULL_CACHE__': True}, ttl=null_ttl)
        
        return data
    
    def get_with_mutex_lock(
        self,
        key: str,
        load_func: callable,
        ttl: int = 1800,
        lock_timeout: int = 10
    ) -> Any:
        """
        带互斥锁的获取方法（防止缓存击穿）
        
        对于热点Key，当缓存失效时只允许一个请求去数据库重建缓存，
        其他请求等待或使用旧数据
        
        Args:
            key: 缓存键名
            load_func: 数据加载函数
            ttl: 缓存时间
            lock_timeout: 锁超时时间（秒）
            
        Returns:
            查询结果
        """
        # 1. 先查缓存
        data = self.get(key)
        if data is not None:
            return data
        
        # 2. 缓存未命中，尝试获取分布式锁
        lock_key = f"lock:{key}"
        lock_acquired = self.set(lock_key, "locked", ttl=lock_timeout, nx=True)
        
        if lock_acquired:
            # 3. 获得锁，查询数据库
            try:
                print(f"🔒 获得锁，正在重建缓存: {key}")
                data = load_func()
                
                if data is not None:
                    # 设置随机TTL防止雪崩
                    actual_ttl = ttl + random.randint(0, ttl // 10)
                    self.set(key, data, ttl=actual_ttl)
                
                return data
                
            finally:
                # 释放锁
                self.delete(lock_key)
        else:
            # 4. 未获得锁，短暂等待后重试
            print(f"⏳ 未获得锁，等待后重试: {key}")
            time.sleep(0.05)  # 50ms
            return self.get_with_mutex_lock(key, load_func, ttl, lock_timeout)
    
    def get_with_random_ttl(
        self,
        key: str,
        load_func: callable,
        base_ttl: int = 1800
    ) -> Any:
        """
        带随机TTL的获取方法（防止缓存雪崩）
        
        在基础TTL上添加随机偏移量，避免大量Key同时过期
        
        Args:
            key: 缓存键名
            load_func: 数据加载函数
            base_ttl: 基础过期时间（秒）
            
        Returns:
            查询结果
        """
        # 查缓存
        data = self.get(key)
        if data is not None:
            return data
        
        # 加载数据
        data = load_func()
        
        if data is not None:
            # 添加±10%随机偏移
            jitter = random.randint(0, base_ttl // 10)
            actual_ttl = base_ttl + jitter
            
            self.set(key, data, ttl=actual_ttl)
            print(f"✅ 设置缓存 [{key}] TTL={actual_ttl}s (base={base_ttl}s, jitter={jitter}s)")
        
        return data
    
    # ===== 工具方法 =====
    
    def clear_all(self, pattern: str = "*") -> int:
        """
        清除匹配模式的所有键（谨慎使用！）
        
        Args:
            pattern: 匹配模式（如 "user:*", "cache:*"）
            
        Returns:
            删除的键数量
        """
        try:
            keys = self.client.keys(pattern)
            if keys:
                count = self.client.delete(*keys)
                print(f"🗑️ 清除了 {count} 个匹配 '{pattern}' 的键")
                return count
            return 0
        except Exception as e:
            print(f"❌ 清除缓存失败: {e}")
            return 0
    
    def get_stats(self) -> Dict[str, Any]:
        """获取Redis统计信息"""
        try:
            info = self.client.info()
            return {
                'connected_clients': info.get('connected_clients', 0),
                'used_memory_human': info.get('used_memory_human', '0B'),
                'total_commands_processed': info.get('total_commands_processed', 0),
                'keyspace_hits': info.get('keyspace_hits', 0),
                'keyspace_misses': info.get('keyspace_misses', 0),
                'db_size': self.client.dbsize(),
                'uptime_seconds': info.get('uptime_in_seconds', 0)
            }
        except Exception as e:
            print(f"❌ 获取统计信息失败: {e}")
            return {}
    
    def ping(self) -> bool:
        """测试连接是否正常"""
        try:
            return self.client.ping()
        except Exception:
            return False
    
    def close(self):
        """关闭连接池"""
        try:
            self.pool.disconnect()
            print("✅ Redis连接池已关闭")
        except Exception as e:
            print(f"❌ 关闭连接池失败: {e}")
    
    # ===== 私有方法 =====
    
    def _serialize(self, value: Any) -> str:
        """序列化值为JSON字符串"""
        if isinstance(value, (str, int, float, bool)):
            return value
        elif isinstance(value, dict):
            return json.dumps(value, ensure_ascii=False)
        elif isinstance(value, list):
            return json.dumps(value, ensure_ascii=False)
        else:
            return json.dumps(str(value), ensure_ascii=False)
    
    def _deserialize(self, value: str) -> Any:
        """反序列化JSON字符串为Python对象"""
        if value is None:
            return None
        
        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            return value


# ===== 便捷工厂函数 =====

def create_redis_cache(
    host: str = 'localhost',
    port: int = 6379,
    **kwargs
) -> RedisCache:
    """
    创建Redis缓存实例的便捷函数
    
    Usage:
        cache = create_redis_cache(host='localhost')
        cache.set('test', {'data': 123}, ttl=3600)
    """
    return RedisCache(host=host, port=port, **kwargs)


# ===== 使用示例 =====

if __name__ == "__main__":
    print("""
╔════════════════════════════════════════╗
║     🗄️ Redis Cache Demo                  ║
║     Day 4 数据库技术应用                 ║
╚════════════════════════════════════════╝
    """)
    
    # 测试连接
    try:
        cache = create_redis_cache()
        
        if cache.ping():
            print("✅ Redis连接成功！\n")
            
            # 基本操作演示
            print("=== 基础操作 ===")
            
            # SET & GET
            cache.set('user:1001', {
                'id': 1001,
                'name': '张三',
                'email': 'zhangsan@example.com'
            }, ttl=300)
            print("✅ 设置缓存 user:1001")
            
            user = cache.get('user:1001')
            print(f"📖 获取缓存: {user}")
            
            # EXISTS
            exists = cache.exists('user:1001')
            print(f"🔍 键是否存在: {exists}")
            
            # TTL
            remaining = cache.ttl('user:1001')
            print(f"⏱️ 剩余过期时间: {remaining}秒")
            
            # DELETE
            deleted = cache.delete('user:1001')
            print(f"🗑️ 删除键: 成功删除{deleted}个\n")
            
            # 批量操作
            print("=== 批量操作 ===")
            batch_data = {
                'product:1': {'name': '商品A', 'price': 99.9},
                'product:2': {'name': '商品B', 'price': 199.9},
                'product:3': {'name': '商品C', 'price': 299.9}
            }
            cache.mset(batch_data, ttl=600)
            print("✅ 批量设置3个产品缓存")
            
            products = cache.mget(['product:1', 'product:2', 'product:3'])
            print(f"📦 批量获取: {products}\n")
            
            # 统计信息
            print("=== Redis状态 ===")
            stats = cache.get_stats()
            for k, v in stats.items():
                print(f"{k}: {v}")
            
            # 清理测试数据
            cache.clear_all('product:*')
            
            print("\n✅ 所有演示完成！")
            
        else:
            print("❌ Redis连接失败，请检查Redis服务是否启动")
            print("   启动命令: docker run -d --name redis -p 6379:6379 redis:alpine")
            
    except ImportError as e:
        print(f"❌ 缺少依赖: {e}")
        print("   安装命令: pip install redis")
    
    finally:
        if 'cache' in locals():
            cache.close()
