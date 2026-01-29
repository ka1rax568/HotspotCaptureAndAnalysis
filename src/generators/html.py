"""
HTML 报告生成器
"""
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from jinja2 import Environment, FileSystemLoader

from src.collectors.base import HotspotItem


class HTMLGenerator:
    """HTML 报告生成器"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.template_dir = Path(__file__).parent.parent.parent / "templates"
        self.output_dir = Path(__file__).parent.parent.parent / "docs"

    def generate(self, items: List[HotspotItem]) -> str:
        """生成 HTML 报告，返回文件路径"""
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # 准备模板数据
        categories = list(set(item.category for item in items))
        template_data = {
            "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "total": len(items),
            "categories": sorted(categories),
            "items": [self._format_item(item) for item in items]
        }

        # 渲染模板
        env = Environment(loader=FileSystemLoader(str(self.template_dir)))
        template = env.get_template("report.html")
        html_content = template.render(**template_data)

        # 写入文件
        output_path = self.output_dir / "index.html"
        output_path.write_text(html_content, encoding="utf-8")

        # 同时保存 JSON 数据
        if self.config.get("json", True):
            self._save_json(items)

        return str(output_path)

    def _format_item(self, item: HotspotItem) -> Dict[str, Any]:
        """格式化单条数据"""
        published = ""
        if item.published_at:
            published = item.published_at.strftime("%m-%d %H:%M")
        return {
            "title": item.title,
            "translated_title": item.translated_title,
            "url": item.url,
            "source": item.source,
            "category": item.category,
            "published_at": published,
            "summary": item.summary
        }

    def _save_json(self, items: List[HotspotItem]):
        """保存 JSON 数据"""
        data = [item.to_dict() for item in items]
        json_path = self.output_dir / "data.json"
        json_path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )
