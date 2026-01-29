"""
配置管理模块
"""
import os
from pathlib import Path
from typing import Any, Dict, List, Optional
import yaml


class Config:
    """配置管理类"""

    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or self._default_config_path()
        self._config: Dict[str, Any] = {}
        self.load()

    def _default_config_path(self) -> str:
        """获取默认配置文件路径"""
        return str(Path(__file__).parent.parent.parent / "config" / "config.yaml")

    def load(self) -> None:
        """加载配置文件"""
        with open(self.config_path, 'r', encoding='utf-8') as f:
            self._config = yaml.safe_load(f)

    @property
    def mode(self) -> str:
        """获取运行模式: api 或 cli"""
        return self._config.get('mode', 'api')

    @property
    def sources(self) -> Dict[str, Any]:
        """获取数据源配置"""
        return self._config.get('sources', {})

    @property
    def ai(self) -> Dict[str, Any]:
        """获取 AI 配置"""
        return self._config.get('ai', {})

    @property
    def output(self) -> Dict[str, Any]:
        """获取输出配置"""
        return self._config.get('output', {})

    def is_source_enabled(self, source_name: str) -> bool:
        """检查数据源是否启用"""
        source = self.sources.get(source_name, {})
        return source.get('enabled', False)

    def get_source_config(self, source_name: str) -> Dict[str, Any]:
        """获取指定数据源的配置"""
        return self.sources.get(source_name, {})
