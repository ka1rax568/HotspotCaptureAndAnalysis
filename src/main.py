"""
热点信息聚合系统 - 主程序入口
"""
import argparse
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import Config
from src.collectors.rss import RSSCollector
from src.collectors.twitter import TwitterCollector
from src.collectors.youtube import YouTubeCollector
from src.processors.api_mode import APIProcessor
from src.processors.cli_mode import CLIProcessor
from src.generators.html import HTMLGenerator


def main():
    parser = argparse.ArgumentParser(description="热点信息聚合系统")
    parser.add_argument("--config", default=None, help="配置文件路径")
    parser.add_argument("--mode", choices=["api", "cli"], help="运行模式")
    args = parser.parse_args()

    # 加载配置
    config = Config(args.config)
    mode = args.mode or config.mode

    print(f"[Main] 运行模式: {mode}")
    print(f"[Main] 开始采集数据...")

    # 采集数据
    all_items = []
    collectors = [
        RSSCollector(config.get_source_config("rss")),
        TwitterCollector(config.get_source_config("twitter")),
        YouTubeCollector(config.get_source_config("youtube")),
    ]

    for collector in collectors:
        if collector.is_enabled():
            print(f"[Main] 采集 {collector.name}...")
            items = collector.collect()
            print(f"[Main] {collector.name} 采集到 {len(items)} 条")
            all_items.extend(items)

    print(f"[Main] 共采集 {len(all_items)} 条数据")

    # AI 处理
    ai_enabled = config.ai.get('enabled', True)
    if all_items and ai_enabled:
        print(f"[Main] 开始 AI 处理...")
        if mode == "cli":
            processor = CLIProcessor(config.ai)
        else:
            processor = APIProcessor(config.ai)
        all_items = processor.process(all_items)
    elif not ai_enabled:
        print(f"[Main] AI 处理已禁用，跳过")

    # 生成报告
    print(f"[Main] 生成 HTML 报告...")
    generator = HTMLGenerator(config.output)
    output_path = generator.generate(all_items)
    print(f"[Main] 报告已生成: {output_path}")


if __name__ == "__main__":
    main()
