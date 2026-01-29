# 热点信息聚合系统

通过 GitHub Actions 定时自动采集多平台热点信息，生成 HTML 报告并部署到 GitHub Pages。

## 功能特性

- **多数据源支持**：RSS、Twitter、YouTube（可配置启用/禁用）
- **AI 处理**：支持 Claude API 翻译和摘要（可选）
- **自动化部署**：GitHub Actions 定时运行 + GitHub Pages 托管
- **可扩展架构**：易于添加新数据源

## 快速开始

### 1. Fork 本仓库

### 2. 配置 Secrets

在仓库 Settings → Secrets and variables → Actions 中添加：

| Secret | 必填 | 说明 |
|--------|------|------|
| `TWITTER_API_KEY` | 否 | Twitter API Key (twitterapi.io) |
| `YOUTUBE_API_KEY` | 否 | YouTube Data API Key |
| `ANTHROPIC_API_KEY` | 否 | Claude API Key（AI处理用） |
| `ANTHROPIC_BASE_URL` | 否 | 自定义 API 地址 |

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
  youtube:
    enabled: true

# AI 处理开关
ai:
  enabled: false  # 设为 true 启用翻译/摘要
```

## 项目结构

```
├── .github/workflows/    # GitHub Actions 工作流
├── config/               # 配置文件
├── src/
│   ├── collectors/       # 数据采集器
│   ├── processors/       # AI 处理器
│   └── generators/       # 报告生成器
├── templates/            # HTML 模板
└── docs/                 # 输出目录 (GitHub Pages)
```

## 本地运行

```bash
pip install -r requirements.txt
python src/main.py
```

## License

MIT
