# 项目差距分析

对比原 n8n 信息聚合器方案与当前 GitHub Actions 实现的差距。

## 功能对比

| 功能 | n8n 原方案 | 当前实现 | 状态 |
|------|-----------|----------|------|
| RSS 采集 | 3个源 | 7个源 | ✅ 已超越 |
| Reddit 采集 | 2个板块 | 4个板块(已禁用) | ⏸️ 待启用 |
| Twitter 采集 | 关注用户 | 关键词搜索 | ✅ 完成 |
| YouTube 采集 | 订阅频道 | 关键词搜索+频道RSS | ✅ 完成 |
| TikTok 采集 | 支持 | 未实现 | ❌ 缺失 |
| AI 翻译 | DeepSeek | LiteLLM + DeepSeek-V3 | ✅ 完成 |
| AI 摘要 | 60-80字 | 20-30字 | ✅ 完成 |
| 数据存储 | 飞书多维表格 | GitHub Pages HTML | ✅ 已替代 |
| 定时触发 | n8n 内置 | GitHub Actions | ✅ 完成 |

## 详细差距

### 1. 数据源配置对比

#### RSS 源

| n8n 原方案 | 当前实现 |
|-----------|----------|
| TechCrunch AI | ✅ TechCrunch AI |
| The Verge AI | ✅ The Verge AI |
| NYTimes AI | ✅ NYTimes AI |
| YouTube频道RSS (3个) | ✅ YouTube频道RSS (3个) |
| - | ✅ Hacker News (新增) |

**当前 RSS 源列表：**
- Hacker News (科技热点)
- TechCrunch AI (AI新闻)
- The Verge AI (AI新闻)
- NYTimes AI (AI新闻)
- AI Explained 频道 (YouTube频道)
- Matthew Berman 频道 (YouTube频道)
- AI Jason 频道 (YouTube频道)

### 2. AI 处理 ✅ 已解决

**n8n 原方案**：
- 使用 DeepSeek 模型（成本低）
- 详细的摘要提示词（60-80字）
- 结构化输出解析

**当前实现**：
- 使用 LiteLLM 统一接口
- 集成硅基流动 DeepSeek-V3 模型
- 简单的摘要提示词（20-30字）
- 支持多种模型切换

#### Reddit

| 配置项 | n8n 原方案 | 当前实现 |
|--------|-----------|----------|
| 板块 | ArtificialInteligence, artificial | artificial, ArtificialInteligence, MachineLearning, LocalLLaMA |
| 过滤 | 24小时内 + 点赞>50 | ✅ 24小时内 + 点赞>50 |
| 状态 | 启用 | ⏸️ 暂时禁用 |

#### Twitter

| 配置项 | n8n 原方案 | 当前实现 |
|--------|-----------|----------|
| 方式 | 关注特定用户 | 关键词搜索 |
| 关键词 | - | AI, ChatGPT, LLM, 机器学习 |
| 数量 | - | 每词30条 |

#### YouTube

| 配置项 | n8n 原方案 | 当前实现 |
|--------|-----------|----------|
| 方式 | 订阅频道 (3个) | 关键词搜索 + 频道RSS |
| 关键词 | - | AI, ChatGPT, LLM |
| 时间 | 24小时/14天 | 可配置 (默认1天) |
| 数量 | - | 每词15条 |

#### TikTok

| n8n 原方案 | 当前实现 |
|-----------|----------|
| ✅ 支持 | ❌ 未实现 |

### 3. 未实现功能

| 功能 | 优先级 | 说明 |
|------|--------|------|
| TikTok 采集 | 中 | n8n 原方案支持 |
| Reddit 启用 | 中 | 代码已完成，需OAuth |
| 飞书同步 | 低 | 原方案存储到飞书 |
| 去重机制 | 中 | 避免重复内容 |
| 热度排序 | 中 | 按互动数据排序 |

## 后续优化建议

1. **短期**：启用 Reddit 采集（需配置 OAuth）
2. **中期**：添加 TikTok 采集器、去重机制
3. **长期**：热度排序、历史归档
