"""
LiteLLM 统一 AI 处理器 - 支持多种模型提供商
"""
import os
import json
from typing import Any, Dict, List

import litellm

from .base import BaseProcessor
from src.collectors.base import HotspotItem
from src.prompts import PromptManager


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
        self.model = config.get('model', 'openai/Qwen/Qwen3-8B')
        self.batch_size = config.get('batch_size', 5)
        self.timeout = config.get('timeout', 120)

        # 初始化 Prompt 管理器
        self.prompt_manager = PromptManager()

        # 批处理配置
        self.max_batch_size = config.get('batch_size', 5)
        self.max_title_chars = config.get('max_title_chars', 500)  # 每批最大字符数

        # 禁用 LiteLLM 的日志输出
        litellm.suppress_debug_info = True

    def _calculate_batch_size(self, items: List[HotspotItem], start_idx: int) -> int:
        """动态计算批次大小，根据标题长度调整"""
        total_chars = 0
        count = 0
        for i in range(start_idx, len(items)):
            title_len = len(items[i].title)
            if total_chars + title_len > self.max_title_chars and count > 0:
                break
            total_chars += title_len
            count += 1
            if count >= self.max_batch_size:
                break
        return max(1, count)

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
        """批量处理热点，支持动态批次大小和失败重试"""
        tasks = self.config.get('tasks', {})
        do_translate = tasks.get('translate', True)
        do_summarize = tasks.get('summarize', True)

        i = 0
        total = len(items)
        while i < total:
            # 动态计算批次大小
            batch_size = self._calculate_batch_size(items, i)
            batch = items[i:i + batch_size]

            print(f"[API] 处理 {i+1}-{i+len(batch)}/{total} 条...")
            success = self._process_batch(batch, do_translate, do_summarize)

            # 如果批处理失败且批次大于1，降级为逐条处理
            if not success and len(batch) > 1:
                print(f"[API] 批处理失败，降级为逐条处理...")
                for item in batch:
                    self._process_batch([item], do_translate, do_summarize)

            i += batch_size

        return items

    def _process_batch(self, batch: List[HotspotItem], translate: bool, summarize: bool) -> bool:
        """处理单批数据，返回是否成功"""
        titles = [item.title for item in batch]
        content = self.prompt_manager.format_content_list(titles)

        prompts = self.prompt_manager.get_prompt(
            task_name='translate_summarize',
            model=self.model,
            variables={'content': content}
        )

        messages = []
        if prompts['system']:
            messages.append({"role": "system", "content": prompts['system']})
        messages.append({"role": "user", "content": prompts['user']})

        try:
            response = litellm.completion(
                model=self.model,
                messages=messages,
                api_key=self.api_key,
                api_base=self.api_base,
                max_tokens=2000
            )
            result_text = response.choices[0].message.content
            return self._parse_results(batch, result_text)
        except Exception as e:
            print(f"[API] 批处理失败: {e}")
            return False

    def _parse_results(self, batch: List[HotspotItem], result_text: str) -> bool:
        """解析AI返回结果，返回是否成功"""
        try:
            start = result_text.find('[')
            end = result_text.rfind(']') + 1
            if start >= 0 and end > start:
                json_str = result_text[start:end]
                results = json.loads(json_str)
                parsed_count = 0
                for r in results:
                    idx = r.get('index', 1) - 1
                    if 0 <= idx < len(batch):
                        batch[idx].translated_title = r.get('translated', '')
                        batch[idx].summary = r.get('summary', '')
                        parsed_count += 1
                # 检查是否所有条目都被处理
                return parsed_count == len(batch)
            return False
        except Exception as e:
            print(f"[API] 解析结果失败: {e}")
            return False
