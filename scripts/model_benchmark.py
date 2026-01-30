#!/usr/bin/env python3
"""
模型对比测试工具 - 用于对比不同 LLM 的翻译和摘要效果

使用方法:
    # 使用真实采集数据对比所有模型
    python scripts/model_benchmark.py

    # 只测试特定模型
    python scripts/model_benchmark.py --models qwen glm

    # 限制测试数据条数
    python scripts/model_benchmark.py --limit 10

    # 只使用 RSS 数据源
    python scripts/model_benchmark.py --source rss
"""
import os
import sys
import json
import time
import argparse
from datetime import datetime
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, asdict

# 添加项目根目录到路径
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

import litellm
litellm.suppress_debug_info = True

from src.config import Config
from src.collectors.rss import RSSCollector
from src.collectors.twitter import TwitterCollector
from src.collectors.youtube import YouTubeCollector
from src.prompts import PromptManager


# ============ 模型配置 ============
MODELS = {
    "qwen": {
        "name": "Qwen3-8B (硅基流动)",
        "model": "openai/Qwen/Qwen3-8B",
        "api_base": "https://api.siliconflow.cn/v1",
        "api_key_env": "AI_API_KEY",
    },
    "glm": {
        "name": "GLM-4-Flash (智谱)",
        "model": "openai/glm-4-flash",
        "api_base": "https://open.bigmodel.cn/api/paas/v4",
        "api_key_env": "ZAI_API_KEY",
    },
    # "deepseek": {
    #     "name": "DeepSeek-V3",
    #     "model": "deepseek/deepseek-chat",
    #     "api_base": "https://api.deepseek.com",
    #     "api_key_env": "DEEPSEEK_API_KEY",
    # },
}


def collect_real_data(limit_per_source: int = 5) -> Dict[str, List[str]]:
    """从项目所有启用的采集器获取真实数据，按来源分组"""
    config_path = os.path.join(PROJECT_ROOT, "config", "config.yaml")
    config = Config(config_path)

    data_by_source = {}

    # RSS 采集
    rss_config = config.get_source_config("rss")
    if rss_config.get("enabled"):
        print("📥 采集 RSS 数据...")
        collector = RSSCollector(rss_config)
        items = collector.collect()
        titles = list(dict.fromkeys([item.title for item in items]))[:limit_per_source]
        if titles:
            data_by_source["RSS"] = titles
            print(f"   RSS: {len(titles)} 条")

    # Twitter 采集
    twitter_config = config.get_source_config("twitter")
    if twitter_config.get("enabled"):
        print("📥 采集 Twitter 数据...")
        collector = TwitterCollector(twitter_config)
        items = collector.collect()
        titles = list(dict.fromkeys([item.title for item in items]))[:limit_per_source]
        if titles:
            data_by_source["Twitter"] = titles
            print(f"   Twitter: {len(titles)} 条")

    # YouTube 采集
    youtube_config = config.get_source_config("youtube")
    if youtube_config.get("enabled"):
        print("📥 采集 YouTube 数据...")
        collector = YouTubeCollector(youtube_config)
        items = collector.collect()
        titles = list(dict.fromkeys([item.title for item in items]))[:limit_per_source]
        if titles:
            data_by_source["YouTube"] = titles
            print(f"   YouTube: {len(titles)} 条")

    return data_by_source


@dataclass
class TestResult:
    """单次测试结果"""
    model_key: str
    model_name: str
    source: str  # 数据来源: RSS, Twitter, YouTube
    title: str
    translated: str
    summary: str
    latency_ms: float
    success: bool
    error: Optional[str] = None


@dataclass
class ModelStats:
    """模型统计数据"""
    model_key: str
    model_name: str
    total_tests: int
    success_count: int
    fail_count: int
    avg_latency_ms: float
    min_latency_ms: float
    max_latency_ms: float


# 初始化 PromptManager
prompt_manager = PromptManager()


def build_prompt(titles: List[str], model: str = None) -> Dict[str, str]:
    """构建测试提示词，返回 system 和 user prompt"""
    content = prompt_manager.format_content_list(titles)
    return prompt_manager.get_prompt(
        task_name='translate_summarize',
        model=model,
        variables={'content': content}
    )


def parse_response(text: str, count: int) -> List[Dict]:
    """解析模型响应"""
    try:
        start = text.find('[')
        end = text.rfind(']') + 1
        if start >= 0 and end > start:
            return json.loads(text[start:end])
    except:
        pass
    return [{"index": i+1, "translated": "", "summary": ""} for i in range(count)]


def test_model(model_key: str, config: Dict, titles: List[str], source: str) -> List[TestResult]:
    """测试单个模型"""
    results = []
    api_key = os.environ.get(config["api_key_env"], "")

    if not api_key:
        print(f"  [跳过] 未设置环境变量 {config['api_key_env']}")
        for title in titles:
            results.append(TestResult(
                model_key=model_key,
                model_name=config["name"],
                source=source,
                title=title,
                translated="",
                summary="",
                latency_ms=0,
                success=False,
                error=f"Missing {config['api_key_env']}"
            ))
        return results

    prompts = build_prompt(titles, config["model"])

    start_time = time.time()
    try:
        messages = []
        if prompts['system']:
            messages.append({"role": "system", "content": prompts['system']})
        messages.append({"role": "user", "content": prompts['user']})

        kwargs = {
            "model": config["model"],
            "messages": messages,
            "api_key": api_key,
            "max_tokens": 2000,
        }
        if config.get("api_base"):
            kwargs["api_base"] = config["api_base"]

        response = litellm.completion(**kwargs)
        latency_ms = (time.time() - start_time) * 1000

        result_text = response.choices[0].message.content
        parsed = parse_response(result_text, len(titles))

        for i, title in enumerate(titles):
            item = next((p for p in parsed if p.get("index") == i+1), {})
            results.append(TestResult(
                model_key=model_key,
                model_name=config["name"],
                source=source,
                title=title,
                translated=item.get("translated", ""),
                summary=item.get("summary", ""),
                latency_ms=latency_ms / len(titles),
                success=True,
            ))

    except Exception as e:
        latency_ms = (time.time() - start_time) * 1000
        for title in titles:
            results.append(TestResult(
                model_key=model_key,
                model_name=config["name"],
                source=source,
                title=title,
                translated="",
                summary="",
                latency_ms=latency_ms / len(titles),
                success=False,
                error=str(e)
            ))

    return results


def calculate_stats(results: List[TestResult]) -> ModelStats:
    """计算模型统计数据"""
    success_results = [r for r in results if r.success]
    latencies = [r.latency_ms for r in success_results] if success_results else [0]

    return ModelStats(
        model_key=results[0].model_key,
        model_name=results[0].model_name,
        total_tests=len(results),
        success_count=len(success_results),
        fail_count=len(results) - len(success_results),
        avg_latency_ms=sum(latencies) / len(latencies),
        min_latency_ms=min(latencies),
        max_latency_ms=max(latencies),
    )


def print_comparison(all_results: Dict[str, List[TestResult]]):
    """打印对比结果"""
    print("\n" + "=" * 80)
    print("模型对比结果")
    print("=" * 80)

    # 统计信息
    print("\n📊 性能统计:")
    print("-" * 60)
    print(f"{'模型':<25} {'成功率':<12} {'平均延迟':<15} {'状态'}")
    print("-" * 60)

    for model_key, results in all_results.items():
        stats = calculate_stats(results)
        success_rate = f"{stats.success_count}/{stats.total_tests}"
        latency = f"{stats.avg_latency_ms:.0f}ms" if stats.success_count > 0 else "N/A"
        status = "✅" if stats.success_count == stats.total_tests else "⚠️" if stats.success_count > 0 else "❌"
        print(f"{stats.model_name:<25} {success_rate:<12} {latency:<15} {status}")

    # 按来源分组显示详细对比
    sources = list(set(r.source for results in all_results.values() for r in results))

    for source in sources:
        print(f"\n📝 [{source}] 翻译对比:")
        print("-" * 80)

        # 获取该来源的标题（取前2条）
        titles = []
        for results in all_results.values():
            for r in results:
                if r.source == source and r.title not in titles:
                    titles.append(r.title)
                    if len(titles) >= 2:
                        break
            if len(titles) >= 2:
                break

        for title in titles:
            # 截断过长的标题
            display_title = title[:60] + "..." if len(title) > 60 else title
            print(f"\n原文: {display_title}")
            for model_key, results in all_results.items():
                result = next((r for r in results if r.title == title), None)
                if result and result.success:
                    print(f"  [{MODELS[model_key]['name'][:12]}]")
                    print(f"    翻译: {result.translated}")
                    print(f"    摘要: {result.summary}")
                else:
                    error = result.error if result else "未测试"
                    print(f"  [{MODELS[model_key]['name'][:12]}] ❌ {error}")


def save_results(all_results: Dict[str, List[TestResult]], output_path: str):
    """保存结果到 JSON"""
    data = {
        "timestamp": datetime.now().isoformat(),
        "results": {k: [asdict(r) for r in v] for k, v in all_results.items()},
        "stats": {k: asdict(calculate_stats(v)) for k, v in all_results.items()},
    }
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"\n💾 结果已保存到: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="模型对比测试工具")
    parser.add_argument("--models", nargs="+", help="要测试的模型 (默认全部)")
    parser.add_argument("--limit", type=int, default=5, help="每个数据源的测试条数 (默认5)")
    parser.add_argument("--output", default="tests/results/benchmark_results.json", help="输出文件")
    args = parser.parse_args()

    # 确定要测试的模型
    model_keys = args.models if args.models else list(MODELS.keys())
    model_keys = [k for k in model_keys if k in MODELS]

    if not model_keys:
        print("❌ 没有有效的模型配置")
        return

    # 采集真实数据（按来源分组）
    print("🚀 模型对比测试\n")
    data_by_source = collect_real_data(limit_per_source=args.limit)

    if not data_by_source:
        print("❌ 未能采集到测试数据")
        return

    total_count = sum(len(titles) for titles in data_by_source.values())
    print(f"\n📊 测试配置:")
    print(f"   模型: {', '.join(model_keys)}")
    print(f"   数据源: {', '.join(data_by_source.keys())}")
    print(f"   总数据: {total_count} 条")
    print()

    # 运行测试（按来源分批测试）
    all_results = {k: [] for k in model_keys}

    for source, titles in data_by_source.items():
        print(f"\n🔄 测试 [{source}] 数据 ({len(titles)} 条)...")
        for model_key in model_keys:
            config = MODELS[model_key]
            print(f"   📡 {config['name']}...")
            results = test_model(model_key, config, titles, source)
            all_results[model_key].extend(results)

            success = sum(1 for r in results if r.success)
            print(f"      完成: {success}/{len(results)} 成功")

    # 输出结果
    print_comparison(all_results)
    save_results(all_results, args.output)


if __name__ == "__main__":
    main()
