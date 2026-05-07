## 项目概述
- **名称**: AI每日新闻订阅
- **功能**: 每天抓取10条AI领域最新新闻，通过飞书机器人推送给用户

### 节点清单
| 节点名 | 文件位置 | 类型 | 功能描述 | 配置文件 |
|-------|---------|------|---------|---------|
| search_news | `graphs/nodes/search_news_node.py` | task | 搜索最近一天的AI领域最新新闻，筛选出10条高质量内容 | - |
| format_news | `graphs/nodes/format_news_node.py` | task | 将搜索到的新闻列表格式化为易读的Markdown格式 | - |
| send_notification | `graphs/nodes/send_notification_node.py` | task | 将格式化后的新闻内容通过飞书机器人推送给用户 | - |

## 技能使用
- 节点`search_news`使用技能`web-search`
- 节点`send_notification`使用技能`feishu-message`

## 工作流说明
1. **search_news**: 使用搜索引擎搜索"AI artificial intelligence 最新新闻"，筛选最近1天内的10条高质量内容
2. **format_news**: 将新闻列表格式化为包含标题、来源、摘要、链接的Markdown格式
3. **send_notification**: 通过飞书webhook发送格式化后的新闻（需配置飞书机器人集成）
