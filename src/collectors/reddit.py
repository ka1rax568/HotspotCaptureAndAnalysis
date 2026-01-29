"""
Reddit 采集器
"""
import os
from datetime import datetime, timezone
from typing import Any, Dict, List
import requests

from .base import BaseCollector, HotspotItem


class RedditCollector(BaseCollector):
    """Reddit 采集器"""

    @property
    def name(self) -> str:
        return "reddit"

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.base_url = "https://www.reddit.com"

    def collect(self) -> List[HotspotItem]:
        if not self.is_enabled():
            return []

        items = []
        subreddits = self.config.get('subreddits', ['artificial'])
        min_score = self.config.get('min_score', 50)
        hours = self.config.get('hours', 24)

        for subreddit in subreddits:
            sub_items = self._fetch_subreddit(subreddit, min_score, hours)
            items.extend(sub_items)

        return items

    def _fetch_subreddit(self, subreddit: str, min_score: int, hours: int) -> List[HotspotItem]:
        """获取单个 subreddit 的热门帖子"""
        try:
            url = f"{self.base_url}/r/{subreddit}/hot.json"
            headers = {"User-Agent": "HotspotAggregator/1.0"}

            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            data = response.json()

            items = []
            now = datetime.now(timezone.utc).timestamp()
            cutoff = now - (hours * 3600)

            for post in data.get('data', {}).get('children', []):
                post_data = post.get('data', {})

                # 过滤：时间和点赞数
                created = post_data.get('created_utc', 0)
                score = post_data.get('ups', 0)

                if created < cutoff or score < min_score:
                    continue

                item = HotspotItem(
                    title=post_data.get('title', ''),
                    url=f"https://www.reddit.com{post_data.get('permalink', '')}",
                    source=f"r/{subreddit}",
                    category="Reddit热点",
                    published_at=self._parse_date(datetime.fromtimestamp(created, tz=timezone.utc).isoformat()),
                    extra={
                        'score': score,
                        'comments': post_data.get('num_comments', 0),
                        'author': post_data.get('author', '')
                    }
                )
                items.append(item)

            return items
        except requests.RequestException as e:
            print(f"[Reddit] 采集 r/{subreddit} 失败: {e}")
            return []
