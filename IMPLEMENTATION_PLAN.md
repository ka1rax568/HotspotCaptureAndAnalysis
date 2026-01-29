# 热点信息聚合系统 - 实现计划

## 项目概述

通过 GitHub Actions 定时触发，使用 Claude AI 抓取和分析多平台热点信息，生成 HTML 报告并部署到 GitHub Pages。

## 技术栈

- **运行环境**: GitHub Actions (Ubuntu)
- **编程语言**: Python 3.11+
- **AI 处理**: Claude API / Claude Code CLI (可切换)
- **部署**: GitHub Pages

## 数据源

| 数据源 | 状态 | 优先级 |
|--------|------|--------|
| RSS | 启用 | P0 |
| Twitter | 启用 | P1 |
| YouTube | 启用 | P2 |
| Reddit | 禁用 | - |

---

## 实现阶段

### 阶段一：基础架构 (P0)

- [x] 创建实现计划文档
- [x] 搭建项目目录结构
- [x] 实现配置管理模块
- [x] 实现数据采集器基类

### 阶段二：数据采集器 (P1)

- [x] RSS 采集器
- [x] Twitter 采集器
- [x] YouTube 采集器

### 阶段三：AI 处理层 (P2)

- [x] API 模式处理器
- [x] CLI 模式处理器

### 阶段四：输出与部署 (P3)

- [x] HTML 报告生成器
- [x] 主程序入口
- [x] GitHub Actions 工作流
- [x] 本地测试验证

---

## 实现记录

### 2025-01-29

**已完成**:
- 创建实现计划文档
- 搭建项目目录结构
- 实现配置管理模块 (`src/config.py`)
- 实现数据采集器基类 (`src/collectors/base.py`)
- 实现 RSS 采集器 (`src/collectors/rss.py`)
- 实现 Twitter 采集器 (`src/collectors/twitter.py`)
- 实现 YouTube 采集器 (`src/collectors/youtube.py`)
- 实现 API 模式处理器 (`src/processors/api_mode.py`)
- 实现 CLI 模式处理器 (`src/processors/cli_mode.py`)
- 实现 HTML 报告生成器 (`src/generators/html.py`)
- 实现主程序入口 (`src/main.py`)
- 创建 GitHub Actions 工作流 (`.github/workflows/daily-hotspot.yml`)

**进行中**:
- 无

**待处理**:
- AI 处理功能修复
- 热度过滤逻辑优化

详细差距分析见 [GAP_ANALYSIS.md](docs/GAP_ANALYSIS.md)

---

## 配置说明

详见 `config/config.yaml`

## 使用方式

```bash
# 本地运行
python src/main.py

# 指定配置
python src/main.py --config config/config.yaml

# 指定模式
python src/main.py --mode api
python src/main.py --mode cli
```
