"""
Claude Code CLI 模式处理器
"""
import json
import subprocess
import tempfile
from typing import Any, Dict, List

from .base import BaseProcessor
from src.collectors.base import HotspotItem


class CLIProcessor(BaseProcessor):
    """使用 Claude Code CLI 的处理器"""

    @property
    def name(self) -> str:
        return "cli"

    def process(self, items: List[HotspotItem]) -> List[HotspotItem]:
        if not items:
            return []

        try:
            return self._process_with_cli(items)
        except Exception as e:
            print(f"[CLI] 处理失败: {e}")
            return items

    def _build_prompt(self, data: List[Dict]) -> str:
        """构建提示词"""
        data_json = json.dumps(data, ensure_ascii=False)
        return f"""请处理以下热点标题，翻译成中文并生成摘要。

数据: {data_json}

返回JSON格式: [{{"index": 0, "translated": "中文", "summary": "摘要"}}]"""

    def _parse_results(self, items: List[HotspotItem], output: str):
        """解析CLI输出"""
        try:
            start = output.find('[')
            end = output.rfind(']') + 1
            if start >= 0 and end > start:
                results = json.loads(output[start:end])
                for r in results:
                    idx = r.get('index', 0)
                    if 0 <= idx < len(items):
                        items[idx].translated_title = r.get('translated', '')
                        items[idx].summary = r.get('summary', '')
        except Exception as e:
            print(f"[CLI] 解析失败: {e}")
        """使用 Claude CLI 处理"""
        # 准备数据
        data = [{"index": i, "title": item.title} for i, item in enumerate(items)]

        # 构建提示
        prompt = self._build_prompt(data)

        # 调用 Claude CLI
        result = subprocess.run(
            ["claude", "--print", "-p", prompt],
            capture_output=True,
            text=True,
            timeout=120
        )

        if result.returncode == 0:
            self._parse_results(items, result.stdout)

        return items
