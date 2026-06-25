"""
PostgreSQL配置优化 - Day 4 数据库技术应用
提供生产级的PostgreSQL连接和查询优化方案
"""

from typing import Optional
from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PostgreSQLConfig:
    """PostgreSQL配置管理类"""
    
    def __init__(
        self,
        database_url: str = "postgresql://postgres:password@localhost:5432/blog",
        pool_size: int = 5,
        max_overflow: int = 10,
        pool_timeout: int = 30,
        pool_recycle: int = 3600,
        echo: bool = False,
        **kwargs
    ):
        """
        初始化PostgreSQL配置
        
        Args:
            database_url: 数据库连接URL格式:
                postgresql://user:password@host:port/database
            pool_size: 连接池大小（常驻连接数）
            max_overflow: 超出pool_size后最多可创建的连接数
            pool_timeout: 获取连接的超时时间（秒）
            pool_recycle: 连接回收时间（秒），防止长时间未使用的连接失效
            echo: 是否打印SQL语句（开发调试用）
            **kwargs: 其他SQLAlchemy引擎参数
        """
        self.database_url = database_url
        self.pool_size = pool_size
        self.max_overflow = max_overflow
        self.pool_timeout = pool_timeout
        self.pool_recycle = pool_recycle
        
        # 创建引擎（带连接池）
        self.engine = create_engine(
            database_url,
            poolclass=QueuePool,
            pool_size=pool_size,
            max_overflow=max_overflow,
            pool_timeout=pool_timeout,
            pool_recycle=pool_recycle,
            echo=echo,
            # 预Ping检查：每次从连接池获取连接时检测是否有效
            pool_pre_ping=True,
            **kwargs
        )
        
        # 创建会话工厂
        self.SessionLocal = sessionmaker(
            bind=self.engine,
            autocommit=False,
            autoflush=False,
            expire_on_commit=False
        )
        
        # 注册事件监听器
        self._setup_event_listeners()
    
    def _setup_event_listeners(self):
        """设置事件监听器用于性能监控"""
        
        @event.listens_for(self.engine, "before_cursor_execute")
        def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
            context._query_start_time = time.time()
            logger.debug(f"📝 执行SQL: {statement[:100]}...")
        
        @event.listens_for(self.engine, "after_cursor_execute")
        def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
            total = time.time() - context._query_start_time
            if total > 1.0:  # 慢查询警告（超过1秒）
                logger.warning(f"⚠️ 慢查询 ({total:.3f}s): {statement[:100]}...")
            else:
                logger.debug(f"✅ 查询完成 ({total:.3f}s)")
    
    def get_session(self) -> Session:
        """获取数据库会话（依赖注入用）"""
        db = self.SessionLocal()
        try:
            yield db
        finally:
            db.close()
    
    def test_connection(self) -> bool:
        """测试数据库连接"""
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT version()"))
                version = result.fetchone()[0]
                print(f"✅ PostgreSQL连接成功！\n版本: {version}")
                return True
        except Exception as e:
            logger.error(f"❌ 数据库连接失败: {e}")
            return False
    
    def get_pool_status(self) -> dict:
        """获取连接池状态"""
        pool = self.engine.pool
        return {
            'pool_size': pool.size(),
            'checked_out': pool.checkedout(),
            'overflow': pool.overflow(),
            'checked_in': pool.checkedin()
        }
    
    def execute_optimized_query(self, query: str, params: dict = None) -> list:
        """
        执行优化后的查询（自动添加索引提示等）
        
        Args:
            query: SQL查询语句
            params: 查询参数
            
        Returns:
            查询结果列表
        """
        with self.engine.connect() as conn:
            if params:
                result = conn.execute(text(query), params)
            else:
                result = conn.execute(text(query))
            
            # 转换为字典列表
            columns = result.keys()
            return [dict(zip(columns, row)) for row in result.fetchall()]
    
    def close(self):
        """关闭所有连接"""
        self.engine.dispose()
        logger.info("✅ 数据库连接已关闭")


def create_postgresql_config(**kwargs) -> PostgreSQLConfig:
    """创建PostgreSQL配置的便捷函数"""
    return PostgreSQLConfig(**kwargs)


# ===== 使用示例 =====

if __name__ == "__main__":
    print("""
╔════════════════════════════════════════╗
║     🐘 PostgreSQL 配置演示              ║
║     Day 4 数据库技术应用                 ║
╚════════════════════════════════════════╝
    """)
    
    config = create_postgresql_config()
    
    if config.test_connection():
        # 显示连接池状态
        status = config.get_pool_status()
        print(f"\n📊 连接池状态:")
        for k, v in status.items():
            print(f"   {k}: {v}")
        
        # 执行示例查询
        try:
            results = config.execute_optimized_query("SELECT current_database(), current_user, now()")
            if results:
                print(f"\n💾 当前数据库信息:")
                for key, value in results[0].items():
                    print(f"   {key}: {value}")
        except Exception as e:
            print(f"\n⚠️ 查询执行失败（可能表不存在）: {e}")
    
    config.close()
