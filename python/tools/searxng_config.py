"""
SearXNG Configuration Manager
管理SearXNG搜索工具的配置
"""

import json
import logging
import os
from pathlib import Path
from typing import Dict, List, Optional, Any


class SearXNGConfig:
    """SearXNG配置管理器"""
    
    def __init__(self, config_file: str = "python/tools/searxng_config.json"):
        self.config_file = Path(config_file)
        self.config = self._load_default_config()
        self._load_config()
    
    def _load_default_config(self) -> Dict[str, Any]:
        """加载默认配置"""
        return {
            "searxng": {
                "url": "http://localhost:8888",
                "api_endpoint": "/search",
                "timeout": 15,
                "max_results": 10,
                "default_engines": ["google", "bing", "duckduckgo", "wikipedia"],
                "default_categories": ["general", "science", "news", "social media"],
                "safe_search": True,
                "language": "zh-CN",
                "format": "json"
            },
            "fallback": {
                "enabled": True,
                "engines": ["google", "bing"],
                "timeout": 10
            },
            "cache": {
                "enabled": True,
                "timeout": 300,  # 5分钟
                "max_size": 100
            },
            "logging": {
                "level": "INFO",
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            }
        }
    
    def _load_config(self):
        """加载配置文件"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                
                # 合并配置
                self._merge_config(self.config, user_config)
                logging.info(f"Loaded SearXNG config from {self.config_file}")
            else:
                # 创建默认配置文件
                self.save_config()
                logging.info(f"Created default SearXNG config at {self.config_file}")
                
        except Exception as e:
            logging.error(f"Failed to load SearXNG config: {e}")
    
    def _merge_config(self, base: Dict, update: Dict):
        """递归合并配置"""
        for key, value in update.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._merge_config(base[key], value)
            else:
                base[key] = value
    
    def save_config(self):
        """保存配置到文件"""
        try:
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            logging.info(f"Saved SearXNG config to {self.config_file}")
        except Exception as e:
            logging.error(f"Failed to save SearXNG config: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值"""
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any):
        """设置配置值"""
        keys = key.split('.')
        config = self.config
        
        # 导航到父级
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        # 设置值
        config[keys[-1]] = value
    
    def get_searxng_url(self) -> str:
        """获取SearXNG URL"""
        return self.get("searxng.url", "http://localhost:8888")
    
    def get_timeout(self) -> int:
        """获取超时时间"""
        return self.get("searxng.timeout", 15)
    
    def get_max_results(self) -> int:
        """获取最大结果数"""
        return self.get("searxng.max_results", 10)
    
    def get_default_engines(self) -> List[str]:
        """获取默认搜索引擎"""
        return self.get("searxng.default_engines", ["google", "bing", "duckduckgo"])
    
    def get_default_categories(self) -> List[str]:
        """获取默认搜索分类"""
        return self.get("searxng.default_categories", ["general"])
    
    def is_fallback_enabled(self) -> bool:
        """是否启用回退搜索"""
        return self.get("fallback.enabled", True)
    
    def get_fallback_engines(self) -> List[str]:
        """获取回退搜索引擎"""
        return self.get("fallback.engines", ["google", "bing"])
    
    def is_cache_enabled(self) -> bool:
        """是否启用缓存"""
        return self.get("cache.enabled", True)
    
    def get_cache_timeout(self) -> int:
        """获取缓存超时时间"""
        return self.get("cache.timeout", 300)
    
    def update_searxng_url(self, url: str):
        """更新SearXNG URL"""
        self.set("searxng.url", url)
        self.save_config()
    
    def update_engines(self, engines: List[str]):
        """更新搜索引擎列表"""
        self.set("searxng.default_engines", engines)
        self.save_config()
    
    def update_categories(self, categories: List[str]):
        """更新搜索分类"""
        self.set("searxng.default_categories", categories)
        self.save_config()
    
    def enable_fallback(self, enabled: bool = True):
        """启用/禁用回退搜索"""
        self.set("fallback.enabled", enabled)
        self.save_config()
    
    def enable_cache(self, enabled: bool = True):
        """启用/禁用缓存"""
        self.set("cache.enabled", enabled)
        self.save_config()
    
    def get_config_summary(self) -> Dict[str, Any]:
        """获取配置摘要"""
        return {
            "searxng_url": self.get_searxng_url(),
            "timeout": self.get_timeout(),
            "max_results": self.get_max_results(),
            "default_engines": self.get_default_engines(),
            "default_categories": self.get_default_categories(),
            "fallback_enabled": self.is_fallback_enabled(),
            "cache_enabled": self.is_cache_enabled(),
            "config_file": str(self.config_file)
        }


# 全局配置实例
searxng_config = SearXNGConfig() 