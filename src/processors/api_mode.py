"""
Claude API 模式处理器
"""
import os
from typing import Any, Dict, List

from .base import BaseProcessor
from src.collectors.base import HotspotItem


class APIProcessor(BaseProcessor):
    """使用 Claude API 直接调用的处理器"""

    @property
    def name(self) -> str:
        return "api"

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.api_key = os.environ.get('ANTHROPIC_API_KEY', '')
        self.base_url = os.environ.get('ANTHROPIC_BASE_URL', None)

    def process(self, items: List[HotspotItem]) -> List[HotspotItem]:
        if not items:
            return []

        if not self.api_key:
            print("[API] 未配置 ANTHROPIC_API_KEY")
            return items

        try:
            import anthropic
            # 支持自定义 base_url
            if self.base_url:
                client = anthropic.Anthropic(api_key=self.api_key, base_url=self.base_url)
            else:
                client = anthropic.Anthropic(api_key=self.api_key)
            return self._batch_process(client, items)
        except Exception as e:
            print(f"[API] 处理失败: {e}")
            return items

    def _batch_process(self, client, items: List[HotspotItem]) -> List[HotspotItem]:
        """批量处理热点"""
        tasks = self.config.get('tasks', {})
        do_translate = tasks.get('translate', True)
        do_summarize = tasks.get('summarize', True)

        batch_size = 5
        for i in range(0, len(items), batch_size):
            batch = items[i:i + batch_size]
            self._process_batch(client, batch, do_translate, do_summarize)

        return items

    def _process_batch(self, client, batch: List[HotspotItem], translate: bool, summarize: bool):
        """处理单批数据"""
        titles = [item.title for item in batch]
        prompt = self._build_prompt(titles, translate, summarize)

        try:
            response = client.messages.create(
                model=self.model,
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}]
            )
            result_text = response.content[0].text
            self._parse_results(batch, result_text)
        except Exception as e:
            print(f"[API] 批处理失败: {e}")

    def _build_prompt(self, titles: List[str], translate: bool, summarize: bool) -> str:
        """构建提示词"""
        tasks_desc = []
        if translate:
            tasks_desc.append("翻译成中文")
        if summarize:
            tasks_desc.append("生成简短摘要(20-30字)")

        titles_text = "\n".join([f"{i+1}. {t}" for i, t in enumerate(titles)])

        return f"""请处理以下标题，{" 并 ".join(tasks_desc)}。

{titles_text}

请按以下JSON格式返回:
[{{"index": 1, "translated": "中文标题", "summary": "摘要"}}]"""

    def _parse_results(self, batch: List[HotspotItem], result_text: str):
        """解析AI返回结果"""
        import json
        try:
            start = result_text.find('[')
            end = result_text.rfind(']') + 1
            if start >= 0 and end > start:
                json_str = result_text[start:end]
                results = json.loads(json_str)
                for r in results:
                    idx = r.get('index', 1) - 1
                    if 0 <= idx < len(batch):
                        batch[idx].translated_title = r.get('translated', '')
                        batch[idx].summary = r.get('summary', '')
        except Exception as e:
            print(f"[API] 解析结果失败: {e}")
