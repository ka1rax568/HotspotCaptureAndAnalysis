"""
数据采集器基类
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

from dateutil import parser as date_parser


@dataclass
class HotspotItem:
    """热点信息数据结构"""
    title: str
    url: str
    source: str
    category: str
    published_at: Optional[datetime] = None
    summary: str = ""
    translated_title: str = ""
    extra: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "title": self.title,
            "url": self.url,
            "source": self.source,
            "category": self.category,
            "published_at": self.published_at.isoformat() if self.published_at else None,
            "summary": self.summary,
            "translated_title": self.translated_title,
            "extra": self.extra
        }


class BaseCollector(ABC):
    """采集器基类"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.enabled = config.get('enabled', False)

    @property
    @abstractmethod
    def name(self) -> str:
        """采集器名称"""
        pass

    @abstractmethod
    def collect(self) -> List[HotspotItem]:
        """执行采集，返回热点列表"""
        pass

    def is_enabled(self) -> bool:
        return self.enabled

    def _parse_date(self, date_str: Optional[str]) -> datetime:
        """解析日期字符串"""
        if date_str:
            try:
                return date_parser.parse(date_str)
            except (ValueError, TypeError):
                pass
        return datetime.now()
