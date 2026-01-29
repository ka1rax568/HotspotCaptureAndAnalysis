"""
AI 处理器基类
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List

from src.collectors.base import HotspotItem


class BaseProcessor(ABC):
    """AI 处理器基类"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.model = config.get('model', 'openai/deepseek-ai/DeepSeek-V3')

    @property
    @abstractmethod
    def name(self) -> str:
        """处理器名称"""
        pass

    @abstractmethod
    def process(self, items: List[HotspotItem]) -> List[HotspotItem]:
        """处理热点数据，返回处理后的列表"""
        pass
