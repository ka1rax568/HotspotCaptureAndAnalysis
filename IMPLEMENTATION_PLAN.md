# 热点信息聚合系统 - 实现计划

## 项目概述

通过 GitHub Actions 定时触发，使用 AI 抓取和分析多平台热点信息，生成 HTML 报告并部署到 GitHub Pages。

## 技术栈

- **运行环境**: GitHub Actions (Ubuntu)
- **编程语言**: Python 3.11+
- **AI 处理**: LiteLLM 统一接口（默认 Qwen3-8B 免费模型）
- **部署**: GitHub Pages

## 数据源

| 数据源 | 状态 | 数量 | 说明 |
|--------|------|------|------|
| RSS | ✅ 启用 | 7源 | Hacker News、TechCrunch、The Verge、NYTimes、3个YouTube频道 |
| Twitter | ✅ 启用 | 4词 | AI、ChatGPT、LLM、机器学习 |
| YouTube | ✅ 启用 | 3词 | AI、ChatGPT、LLM |
| Reddit | ⏸️ 禁用 | 4板块 | 代码已完成，待OAuth认证 |

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

### 2025-01-30 (续)

**已完成**:
- 扩展数据源配置（RSS 7源、Twitter 4词、YouTube 3词）
- 新增 Reddit 采集器（支持热度过滤）
- 切换 AI 模型到 Qwen3-8B（免费）
- 添加请求延迟避免 API 限流
- 代码重构：提取公共方法、统一配置管理
- 全面更新项目文档

### 2025-01-30

**已完成**:
- 重构 AI 处理模块，使用 LiteLLM 统一接口
- 集成硅基流动 DeepSeek-V3 模型
- 修复模型名称配置问题
- 更新 GitHub Actions 工作流使用 AI_API_KEY 环境变量

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
- 启用 Reddit（需OAuth认证）
- TikTok 采集器
- 去重机制

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
