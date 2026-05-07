## 项目概述
- **名称**: AI每日新闻订阅
- **功能**: 每天抓取近3天AI领域最新新闻，通过飞书机器人推送给用户（不限条数）

### 节点清单
| 节点名 | 文件位置 | 类型 | 功能描述 | 配置文件 |
|-------|---------|------|---------|---------|
| search_news | `graphs/nodes/search_news_node.py` | task | 搜索近3天的AI领域新闻（GDELT），筛选高质量内容，无条数限制 | - |
| format_news | `graphs/nodes/format_news_node.py` | task | 将搜索到的新闻列表格式化为易读的Markdown格式 | - |
| send_notification | `graphs/nodes/send_notification_node.py` | task | 将格式化后的新闻内容通过飞书机器人推送给用户 | - |

## 定时任务配置

如需每天早上10点自动推送，可通过以下方式配置：

### 方式一：Coze平台定时触发器（推荐）
在Coze平台上为工作流添加定时触发器：
- Cron表达式：`0 10 * * *`

### 方式二：服务器Cron Job
```bash
# 编辑 crontab
crontab -e

# 添加定时任务（每天10点执行）
0 10 * * * cd /workspace/projects && /workspace/projects/.venv/bin/python /workspace/projects/scripts/scheduled_run.py >> /tmp/ai_news_cron.log 2>&1
```

定时执行脚本位置：`scripts/scheduled_run.py`

## 技能使用
- 节点`search_news`使用技能`web-search`
- 节点`send_notification`使用技能`feishu-message`

## 工作流说明
1. **search_news**: 使用GDELT搜索"AI product launch artificial intelligence game app"，筛选近3天内的高质量新闻，无条数限制
2. **format_news**: 将新闻列表格式化为包含标题、来源、摘要、链接的Markdown格式
3. **send_notification**: 通过飞书webhook发送格式化后的新闻（需配置飞书机器人集成）
