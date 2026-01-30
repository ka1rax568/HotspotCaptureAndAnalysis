# 热点信息聚合系统

通过 GitHub Actions 定时自动采集多平台热点信息，使用 AI 进行翻译和摘要，生成 HTML 报告并部署到 GitHub Pages。

## 功能特性

- **多数据源支持**：RSS(7源)、Twitter、YouTube、Reddit(待启用)
- **AI 处理**：基于 LiteLLM 统一接口，支持 Qwen3-8B、GLM-4-Flash 等免费模型
- **Prompt 管理系统**：任务驱动的 Prompt 配置，支持多任务（翻译、摘要、分类、排序等）
- **智能批处理**：动态批次大小，失败自动降级重试
- **自动化部署**：GitHub Actions 定时运行 + GitHub Pages 托管
- **可扩展架构**：易于添加新数据源和 AI 模型
- **限流保护**：内置请求延迟和超时设置，避免 API 限流

## 快速开始

### 1. Fork 本仓库

### 2. 配置 Secrets

在仓库 Settings → Secrets and variables → Actions 中添加：

| Secret | 必填 | 说明 |
|--------|------|------|
| `AI_API_KEY` | 是 | 硅基流动 API Key（Qwen3-8B 免费） |
| `ZAI_API_KEY` | 否 | 智谱 API Key（GLM-4-Flash 免费） |
| `TWITTER_API_KEY` | 否 | Twitter API Key (twitterapi.io) |
| `YOUTUBE_API_KEY` | 否 | YouTube Data API Key |

### 3. 启用 GitHub Pages

Settings → Pages → Source 选择 `gh-pages` branch

### 4. 运行工作流

Actions → "热点信息聚合" → Run workflow

## 配置说明

编辑 `config/config.yaml` 自定义配置：

```yaml
# 数据源开关
sources:
  rss:
    enabled: true
  twitter:
    enabled: true
    delay: 1.5  # 请求间隔(秒)
  youtube:
    enabled: true

# AI 处理配置
ai:
  enabled: true
  model: "openai/Qwen/Qwen3-8B"  # 免费模型
  api_base: "https://api.siliconflow.cn/v1"
```

## 项目结构

```
├── .github/workflows/    # GitHub Actions 工作流
├── config/
│   ├── config.yaml       # 主配置文件
│   └── prompts.yaml      # Prompt 配置文件
├── src/
│   ├── collectors/       # 数据采集器
│   ├── processors/       # AI 处理器
│   ├── prompts/          # Prompt 管理模块
│   └── generators/       # 报告生成器
├── scripts/              # 工具脚本
├── templates/            # HTML 模板
├── tests/results/        # 测试结果（不提交）
└── docs/                 # 输出目录 (GitHub Pages)
```

## 本地运行

```bash
pip install -r requirements.txt
python -m src.main
```

## 工具脚本

```bash
# 切换 AI 模型
python scripts/switch_model.py list    # 列出可用模型
python scripts/switch_model.py qwen    # 切换到 Qwen3-8B
python scripts/switch_model.py glm     # 切换到 GLM-4-Flash

# 模型对比测试
python scripts/model_benchmark.py --limit 5
```

## License

MIT
