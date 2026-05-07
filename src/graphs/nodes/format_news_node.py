"""
新闻格式化节点 - 使用LLM将标题改写为一句话摘要
"""
import json
import logging
from datetime import datetime
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.runnables import RunnableConfig
from langgraph.runtime import Runtime
from coze_coding_utils.runtime_ctx.context import Context
from coze_coding_dev_sdk import LLMClient

from graphs.state import FormatNewsInput, FormatNewsOutput

logger = logging.getLogger(__name__)


def format_news_node(
    state: FormatNewsInput,
    config: RunnableConfig,
    runtime: Runtime[Context]
) -> FormatNewsOutput:
    """
    title: 新闻格式化
    desc: 将新闻标题用LLM改写为一句话摘要，生成易读的Markdown格式
    integrations: 大语言模型
    """
    ctx = runtime.context
    news_list = state.news_list
    today = datetime.now().strftime("%Y年%m月%d日")

    if not news_list:
        formatted_lines = [
            f"# 🤖 AI 每日新闻速递",
            f"**{today}**\n",
            "---",
            "",
            "今日暂无相关新闻。",
            ""
        ]
        return FormatNewsOutput(formatted_news="\n".join(formatted_lines))

    # 构建新闻列表给LLM改写
    news_for_summary = []
    for i, news in enumerate(news_list, 1):
        title = news.get("title_cn", news.get("title", ""))
        if title:
            news_for_summary.append({
                "index": i,
                "title": title,
                "url": news.get("url", "")
            })

    if not news_for_summary:
        return FormatNewsOutput(formatted_news=f"# 🤖 AI 每日新闻速递\n**{today}**\n\n今日暂无有效新闻。")

    # 调用LLM将标题改写为一句话摘要
    news_items_text = "\n".join([
        f"[{item['index']}] {item['title']}"
        for item in news_for_summary
    ])

    prompt = f"""请将以下新闻标题改写为简洁的一句话摘要（每条20-40字），一句话概括新闻的核心内容。

要求：
1. 直接提取或概括新闻的核心信息
2. 语言简洁，准确反映新闻要点
3. 不要添加前缀如"据悉"、"今日"等

输出格式：JSON数组，每项包含index和summary
示例：[{{"index": 1, "summary": "核心内容概括"}}]

新闻列表：
{news_items_text}

请直接输出JSON数组："""

    try:
        client = LLMClient(ctx=ctx)
        messages = [
            SystemMessage(content="你是一个专业的新闻编辑，擅长将新闻标题改写为简洁准确的摘要。"),
            HumanMessage(content=prompt)
        ]
        
        response = client.invoke(messages=messages, temperature=0.3)
        
        content = response.content
        if isinstance(content, str):
            text = content.strip()
        elif isinstance(content, list):
            text = " ".join([
                item.get("text", "") if isinstance(item, dict) else str(item)
                for item in content
            ])
        else:
            text = str(content)
        
        # 清理Markdown代码块
        if text.startswith("```"):
            lines = text.split("\n")
            text = "\n".join(lines[1:-1] if lines[-1] == "```" else lines[1:])
        
        # 解析JSON
        summaries = json.loads(text.strip())
        
        # 构建摘要映射
        summary_map = {}
        for item in summaries:
            summary_map[item["index"]] = item["summary"]
        
    except Exception as e:
        logger.warning(f"LLM改写失败，使用原始标题: {e}")
        # 降级：使用原始标题
        summary_map = {item["index"]: item["title"] for item in news_for_summary}

    # 构建格式化输出
    formatted_lines = [
        f"# 🤖 AI 每日新闻速递",
        f"**{today}**\n",
        "---",
        ""
    ]

    for item in news_for_summary:
        idx = item["index"]
        summary = summary_map.get(idx, item["title"])
        url = item["url"]
        
        formatted_lines.append(f"**{idx}. {summary}**")
        if url:
            formatted_lines.append(f"🔗 [阅读原文]({url})")
        formatted_lines.append("")

    formatted_news = "\n".join(formatted_lines)

    return FormatNewsOutput(formatted_news=formatted_news)
