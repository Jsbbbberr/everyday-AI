"""
行业总结节点 - 根据当日新闻生成行业洞察总结
"""
import json
import logging
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.runnables import RunnableConfig
from langgraph.runtime import Runtime
from coze_coding_utils.runtime_ctx.context import Context
from coze_coding_dev_sdk import LLMClient

from graphs.state import SummaryNewsInput, SummaryNewsOutput

logger = logging.getLogger(__name__)


def summary_news_node(
    state: SummaryNewsInput,
    config: RunnableConfig,
    runtime: Runtime[Context]
) -> SummaryNewsOutput:
    """
    title: 行业总结生成
    desc: 根据当日新闻生成行业洞察总结
    integrations: 大语言模型
    """
    ctx = runtime.context
    news_list = state.news_list

    if not news_list:
        return SummaryNewsOutput(news_summary="今日暂无AI相关新闻。")

    # 构建新闻摘要用于总结
    news_text = "\n".join([
        f"{i+1}. {item.get('title', '')}"
        for i, item in enumerate(news_list)
    ])

    prompt = f"""你是一个专业的AI行业分析师。请根据以下今日AI新闻，总结当前行业状态和风向。

要求：
1. 提炼2-3个最核心的趋势或动态
2. 分析背后的原因和影响
3. 展望未来发展方向
4. 语言简洁专业，适合每日简报

格式：一段200-300字的中文总结段落

今日新闻列表：
{news_text}

请直接输出总结内容，不需要标题："""

    try:
        client = LLMClient(ctx=ctx)
        messages = [
            SystemMessage(content="你是一个专业的AI行业分析师，擅长提炼关键信息和趋势分析。"),
            HumanMessage(content=prompt)
        ]
        
        response = client.invoke(messages=messages, temperature=0.3)
        
        # 解析响应
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
        
        summary = text.strip()
        
        logger.info(f"生成行业总结成功，长度: {len(summary)}")
        return SummaryNewsOutput(news_summary=summary)
        
    except Exception as e:
        logger.error(f"生成行业总结失败: {e}")
        return SummaryNewsOutput(news_summary="今日总结生成失败，请查看详细新闻。")
