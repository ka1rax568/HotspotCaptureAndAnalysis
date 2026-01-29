"""
LiteLLM 统一 AI 处理器 - 支持多种模型提供商
"""
import os
import json
from typing import Any, Dict, List

import litellm

from .base import BaseProcessor
from src.collectors.base import HotspotItem


class APIProcessor(BaseProcessor):
    """使用 LiteLLM 的统一 AI 处理器，支持 OpenAI/Anthropic/DeepSeek 等"""

    @property
    def name(self) -> str:
        return "api"

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        # 从环境变量获取 API Key
        api_key_env = config.get('api_key_env', 'AI_API_KEY')
        self.api_key = os.environ.get(api_key_env, '')
        self.api_base = config.get('api_base')
        self.model = config.get('model', 'openai/deepseek-chat')

        # 禁用 LiteLLM 的日志输出
        litellm.suppress_debug_info = True

    def process(self, items: List[HotspotItem]) -> List[HotspotItem]:
        if not items:
            return []

        if not self.api_key:
            api_key_env = self.config.get('api_key_env', 'AI_API_KEY')
            print(f"[API] 未配置 {api_key_env} 环境变量")
            return items

        print(f"[API] 使用模型: {self.model}")
        if self.api_base:
            print(f"[API] API 地址: {self.api_base}")

        try:
            return self._batch_process(items)
        except Exception as e:
            print(f"[API] 处理失败: {e}")
            return items

    def _batch_process(self, items: List[HotspotItem]) -> List[HotspotItem]:
        """批量处理热点"""
        tasks = self.config.get('tasks', {})
        do_translate = tasks.get('translate', True)
        do_summarize = tasks.get('summarize', True)

        batch_size = 5
        for i in range(0, len(items), batch_size):
            batch = items[i:i + batch_size]
            self._process_batch(batch, do_translate, do_summarize)

        return items

    def _process_batch(self, batch: List[HotspotItem], translate: bool, summarize: bool):
        """处理单批数据"""
        titles = [item.title for item in batch]
        prompt = self._build_prompt(titles, translate, summarize)

        try:
            response = litellm.completion(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                api_key=self.api_key,
                api_base=self.api_base,
                max_tokens=2000
            )
            result_text = response.choices[0].message.content
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
