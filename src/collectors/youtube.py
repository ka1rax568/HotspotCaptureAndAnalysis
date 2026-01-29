"""
YouTube 采集器
"""
import os
from datetime import datetime, timedelta
from typing import Any, Dict, List
import requests
from dateutil import parser as date_parser

from .base import BaseCollector, HotspotItem


class YouTubeCollector(BaseCollector):
    """YouTube 采集器"""

    @property
    def name(self) -> str:
        return "youtube"

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.api_key = os.environ.get('YOUTUBE_API_KEY', '')
        self.search_url = "https://www.googleapis.com/youtube/v3/search"
        self.videos_url = "https://www.googleapis.com/youtube/v3/videos"

    def collect(self) -> List[HotspotItem]:
        if not self.is_enabled():
            return []

        if not self.api_key:
            print("[YouTube] 未配置 API Key")
            return []

        items = []
        queries = self.config.get('queries', ['AI'])
        max_results = self.config.get('max_results', 10)

        for query in queries:
            query_items = self._search(query, max_results)
            items.extend(query_items)

        return items

    def _search(self, query: str, max_results: int) -> List[HotspotItem]:
        """搜索视频"""
        try:
            # 搜索最近24小时的视频
            published_after = (datetime.utcnow() - timedelta(days=1)).isoformat() + "Z"

            params = {
                "part": "snippet",
                "q": query,
                "type": "video",
                "order": "viewCount",
                "publishedAfter": published_after,
                "maxResults": max_results,
                "key": self.api_key
            }

            response = requests.get(self.search_url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()

            # 获取视频ID列表
            video_ids = [item['id']['videoId'] for item in data.get('items', [])]
            if not video_ids:
                return []

            # 获取视频统计信息
            stats = self._get_video_stats(video_ids)

            items = []
            for item in data.get('items', []):
                video_id = item['id']['videoId']
                snippet = item['snippet']
                video_stats = stats.get(video_id, {})

                hotspot = HotspotItem(
                    title=snippet.get('title', ''),
                    url=f"https://www.youtube.com/watch?v={video_id}",
                    source="YouTube",
                    category="YouTube热点",
                    published_at=self._parse_date(snippet.get('publishedAt')),
                    extra={
                        'channel': snippet.get('channelTitle', ''),
                        'views': video_stats.get('viewCount', 0),
                        'likes': video_stats.get('likeCount', 0)
                    }
                )
                items.append(hotspot)

            return items
        except Exception as e:
            print(f"[YouTube] 搜索 '{query}' 失败: {e}")
            return []

    def _get_video_stats(self, video_ids: List[str]) -> Dict[str, Dict]:
        """获取视频统计信息"""
        try:
            params = {
                "part": "statistics",
                "id": ",".join(video_ids),
                "key": self.api_key
            }
            response = requests.get(self.videos_url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()

            stats = {}
            for item in data.get('items', []):
                stats[item['id']] = item.get('statistics', {})
            return stats
        except Exception as e:
            print(f"[YouTube] 获取统计信息失败: {e}")
            return {}

    def _parse_date(self, date_str: str) -> datetime:
        """解析日期"""
        if date_str:
            try:
                return date_parser.parse(date_str)
            except:
                pass
        return datetime.now()
