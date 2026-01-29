"""
RSS 采集器
"""
from datetime import datetime
from typing import Any, Dict, List
import feedparser
from dateutil import parser as date_parser

from .base import BaseCollector, HotspotItem


class RSSCollector(BaseCollector):
    """RSS 源采集器"""

    @property
    def name(self) -> str:
        return "rss"

    def collect(self) -> List[HotspotItem]:
        if not self.is_enabled():
            return []

        items = []
        feeds = self.config.get('feeds', [])

        for feed_config in feeds:
            feed_items = self._collect_feed(feed_config)
            items.extend(feed_items)

        return items

    def _collect_feed(self, feed_config: Dict[str, Any]) -> List[HotspotItem]:
        """采集单个 RSS 源"""
        url = feed_config.get('url', '')
        name = feed_config.get('name', 'Unknown')
        category = feed_config.get('category', 'RSS')

        try:
            feed = feedparser.parse(url)
            items = []

            for entry in feed.entries[:20]:  # 限制每个源最多20条
                published = self._parse_date(entry)
                item = HotspotItem(
                    title=entry.get('title', ''),
                    url=entry.get('link', ''),
                    source=name,
                    category=category,
                    published_at=published,
                    extra={
                        'author': entry.get('author', ''),
                        'tags': [t.term for t in entry.get('tags', [])]
                    }
                )
                items.append(item)

            return items
        except Exception as e:
            print(f"[RSS] 采集 {name} 失败: {e}")
            return []

    def _parse_date(self, entry) -> datetime:
        """解析日期"""
        date_str = entry.get('published') or entry.get('updated')
        if date_str:
            try:
                return date_parser.parse(date_str)
            except:
                pass
        return datetime.now()
