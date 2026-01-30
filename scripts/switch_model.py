#!/usr/bin/env python3
"""
快速切换 AI 模型配置

使用方法:
    python scripts/switch_model.py qwen    # 切换到 Qwen3-8B
    python scripts/switch_model.py glm     # 切换到 GLM-4.7-Flash
    python scripts/switch_model.py list    # 列出所有可用模型
"""
import os
import sys
import yaml

CONFIG_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "config", "config.yaml"
)

MODELS = {
    "qwen": {
        "name": "Qwen3-8B (硅基流动 免费)",
        "model": "openai/Qwen/Qwen3-8B",
        "api_base": "https://api.siliconflow.cn/v1",
        "api_key_env": "AI_API_KEY",
    },
    "glm": {
        "name": "GLM-4-Flash (智谱 免费)",
        "model": "openai/glm-4-flash",
        "api_base": "https://open.bigmodel.cn/api/paas/v4",
        "api_key_env": "ZAI_API_KEY",
    },
    "deepseek": {
        "name": "DeepSeek-V3 (硅基流动)",
        "model": "openai/deepseek-ai/DeepSeek-V3",
        "api_base": "https://api.siliconflow.cn/v1",
        "api_key_env": "AI_API_KEY",
    },
}


def load_config():
    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def save_config(config):
    with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
        yaml.dump(config, f, allow_unicode=True, default_flow_style=False, sort_keys=False)


def get_current_model(config):
    model = config.get('ai', {}).get('model', '')
    for key, m in MODELS.items():
        if m['model'] == model:
            return key, m['name']
    return None, model


def switch_model(model_key: str):
    if model_key not in MODELS:
        print(f"❌ 未知模型: {model_key}")
        print(f"   可用: {', '.join(MODELS.keys())}")
        return False

    config = load_config()
    model_config = MODELS[model_key]

    config['ai']['model'] = model_config['model']
    config['ai']['api_key_env'] = model_config['api_key_env']
    config['ai']['api_base'] = model_config['api_base']

    save_config(config)
    print(f"✅ 已切换到: {model_config['name']}")
    print(f"   环境变量: {model_config['api_key_env']}")
    return True


def list_models():
    config = load_config()
    current_key, current_name = get_current_model(config)

    print("可用模型:")
    print("-" * 50)
    for key, m in MODELS.items():
        marker = " ← 当前" if key == current_key else ""
        print(f"  {key:<10} {m['name']}{marker}")
    print("-" * 50)
    print(f"\n切换: python scripts/switch_model.py <模型名>")


def main():
    if len(sys.argv) < 2 or sys.argv[1] == "list":
        list_models()
    else:
        switch_model(sys.argv[1])


if __name__ == "__main__":
    main()
