from datetime import datetime
from typing import Any, Dict, Optional
from loguru import logger

class CacheManager:
    """缓存管理器"""
    
    def __init__(self, cache_timeout: int = 24 * 3600):
        """初始化缓存管理器
        
        Args:
            cache_timeout (int): 缓存超时时间(秒)，默认24小时
        """
        self._cache_data: Dict[str, Any] = {}
        self._cache_timestamp: Dict[str, datetime] = {}
        self.cache_timeout = cache_timeout
    
    def get_cache_key(self, prefix: str, *args) -> str:
        """生成缓存key
        
        Args:
            prefix (str): 前缀标识
            *args: 可变参数，用于构建唯一key
            
        Returns:
            str: 缓存key
        """
        return f"{prefix}_{'_'.join(map(str, args))}"
    
    def get(self, key: str) -> Optional[Any]:
        """获取缓存数据
        
        Args:
            key (str): 缓存key
            
        Returns:
            Optional[Any]: 缓存数据，如果不存在或已过期返回None
        """
        if not self.is_valid(key):
            return None
        return self._cache_data.get(key)
    
    def set(self, key: str, value: Any) -> None:
        """设置缓存数据
        
        Args:
            key (str): 缓存key
            value (Any): 缓存数据
        """
        self._cache_data[key] = value
        self._cache_timestamp[key] = datetime.now()
        logger.debug(f"Cache set for key: {key}")
    
    def is_valid(self, key: str) -> bool:
        """检查缓存是否有效
        
        Args:
            key (str): 缓存key
            
        Returns:
            bool: 是否有效
        """
        if key not in self._cache_timestamp:
            return False
        
        cache_time = self._cache_timestamp.get(key)
        return (datetime.now() - cache_time).total_seconds() < self.cache_timeout
    
    def clear(self, key: str) -> None:
        """清除指定缓存
        
        Args:
            key (str): 缓存key
        """
        if key in self._cache_data:
            del self._cache_data[key]
        if key in self._cache_timestamp:
            del self._cache_timestamp[key]
        logger.debug(f"Cache cleared for key: {key}")
    
    def clear_all(self) -> None:
        """清除所有缓存"""
        self._cache_data.clear()
        self._cache_timestamp.clear()
        logger.debug("All cache cleared")