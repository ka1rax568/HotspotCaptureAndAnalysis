"""
Twitter 采集器
"""
import os
from datetime import datetime
from typing import Any, Dict, List
import requests
from dateutil import parser as date_parser

from .base import BaseCollector, HotspotItem


class TwitterCollector(BaseCollector):
    """Twitter 采集器 (使用 twitterapi.io)"""

    @property
    def name(self) -> str:
        return "twitter"

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.api_key = os.environ.get('TWITTER_API_KEY', '')
        self.base_url = "https://api.twitterapi.io/twitter/tweet/advanced_search"

    def collect(self) -> List[HotspotItem]:
        if not self.is_enabled():
            return []

        if not self.api_key:
            print("[Twitter] 未配置 API Key")
            return []

        items = []
        queries = self.config.get('queries', ['AI'])
        max_results = self.config.get('max_results', 20)

        for query in queries:
            query_items = self._search(query, max_results)
            items.extend(query_items)

        return items

    def _search(self, query: str, max_results: int) -> List[HotspotItem]:
        """搜索推文"""
        try:
            headers = {"X-API-Key": self.api_key}
            params = {
                "query": query,
                "queryType": "Top"
            }

            response = requests.get(
                self.base_url,
                headers=headers,
                params=params,
                timeout=30
            )
            response.raise_for_status()
            data = response.json()

            items = []
            tweets = data.get('tweets', [])[:max_results]

            for tweet in tweets:
                published = self._parse_date(tweet.get('createdAt'))
                item = HotspotItem(
                    title=tweet.get('text', ''),
                    url=tweet.get('url', ''),
                    source="Twitter",
                    category="Twitter热点",
                    published_at=published,
                    extra={
                        'likes': tweet.get('likeCount', 0),
                        'retweets': tweet.get('retweetCount', 0),
                        'views': tweet.get('viewCount', 0)
                    }
                )
                items.append(item)

            return items
        except Exception as e:
            print(f"[Twitter] 搜索 '{query}' 失败: {e}")
            return []

    def _parse_date(self, date_str: str) -> datetime:
        """解析 Twitter 日期格式"""
        if date_str:
            try:
                return date_parser.parse(date_str)
            except:
                pass
        return datetime.now()
