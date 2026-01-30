"""
Prompt 管理器 - 支持任务驱动的 prompt 加载和渲染
"""
import os
from typing import Any, Dict, List, Optional
import yaml


class PromptManager:
    """Prompt 管理器"""

    def __init__(self, config_path: str = None):
        """初始化 Prompt 管理器"""
        if config_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            config_path = os.path.join(base_dir, 'config', 'prompts.yaml')

        self.config_path = config_path
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        if not os.path.exists(self.config_path):
            return {'settings': {}, 'tasks': {}}

        with open(self.config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f) or {}

    def get_task_list(self) -> List[str]:
        """获取所有可用任务列表"""
        return list(self.config.get('tasks', {}).keys())

    def get_task_info(self, task_name: str) -> Optional[Dict[str, Any]]:
        """获取任务信息"""
        return self.config.get('tasks', {}).get(task_name)

    def get_prompt(
        self,
        task_name: str,
        model: str = None,
        variables: Dict[str, Any] = None
    ) -> Dict[str, str]:
        """
        获取指定任务的 prompt

        Args:
            task_name: 任务名称
            model: 模型名称（可选，用于获取模型特定配置）
            variables: 变量字典，用于替换 prompt 中的占位符

        Returns:
            包含 system 和 user prompt 的字典
        """
        task_config = self.get_task_info(task_name)
        if not task_config:
            raise ValueError(f"未知任务: {task_name}")

        # 获取默认配置
        default = task_config.get('default', {})
        system_prompt = default.get('system', '')
        user_prompt = default.get('user', '')

        # 如果指定了模型，尝试获取模型特定配置
        if model:
            model_key = self._normalize_model_key(model)
            models_config = task_config.get('models', {})
            if model_key in models_config:
                model_config = models_config[model_key]
                # 模型配置覆盖默认配置
                if 'system' in model_config:
                    system_prompt = model_config['system']
                if 'user' in model_config:
                    user_prompt = model_config['user']

        # 变量替换
        if variables:
            system_prompt = self._render_template(system_prompt, variables)
            user_prompt = self._render_template(user_prompt, variables)

        return {
            'system': system_prompt.strip(),
            'user': user_prompt.strip()
        }

    def _normalize_model_key(self, model: str) -> str:
        """标准化模型名称为配置键"""
        model_lower = model.lower()
        if 'qwen' in model_lower:
            return 'qwen'
        elif 'glm' in model_lower:
            return 'glm'
        elif 'deepseek' in model_lower:
            return 'deepseek'
        return model_lower

    def _render_template(self, template: str, variables: Dict[str, Any]) -> str:
        """渲染模板，替换变量"""
        result = template
        for key, value in variables.items():
            placeholder = '{' + key + '}'
            if placeholder in result:
                result = result.replace(placeholder, str(value))
        return result

    def format_content_list(self, items: List[str]) -> str:
        """格式化内容列表为编号文本"""
        return '\n'.join([f"{i+1}. {item}" for i, item in enumerate(items)])
