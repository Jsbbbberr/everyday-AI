"""
新闻格式化节点 - 使用翻译后的内容
"""
from datetime import datetime
from langchain_core.runnables import RunnableConfig
from langgraph.runtime import Runtime
from coze_coding_utils.runtime_ctx.context import Context

from graphs.state import FormatNewsInput, FormatNewsOutput


def format_news_node(
    state: FormatNewsInput,
    config: RunnableConfig,
    runtime: Runtime[Context]
) -> FormatNewsOutput:
    """
    title: 新闻格式化
    desc: 将翻译后的新闻列表格式化为易读的Markdown格式
    integrations: 
    """
    news_list = state.news_list
    today = datetime.now().strftime("%Y年%m月%d日")

    formatted_lines = [
        f"# 🤖 AI 每日新闻速递",
        f"**{today}**\n",
        "---",
        ""
    ]

    for idx, news in enumerate(news_list, 1):
        # 优先使用中文标题
        title = news.get("title_cn", news.get("title", "无标题"))
        url = news.get("url", "")
        source = news.get("source", news.get("site_name", ""))
        # 优先使用中文摘要
        description = news.get("description_cn", news.get("description", news.get("snippet", "")))

        formatted_lines.append(f"**{idx}. {title}**")
        if source:
            formatted_lines.append(f"📍 来源: {source}")
        if description:
            desc_text = description[:300] + "..." if len(description) > 300 else description
            formatted_lines.append(f"📝 {desc_text}")
        if url:
            formatted_lines.append(f"🔗 [阅读原文]({url})")
        formatted_lines.append("")

    formatted_news = "\n".join(formatted_lines)

    return FormatNewsOutput(formatted_news=formatted_news)
