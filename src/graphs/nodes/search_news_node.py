"""
AI新闻搜索节点
"""
from langchain_core.runnables import RunnableConfig
from langgraph.runtime import Runtime
from coze_coding_utils.runtime_ctx.context import Context
from coze_coding_dev_sdk import SearchClient
from coze_coding_utils.runtime_ctx.context import new_context

from graphs.state import SearchNewsInput, SearchNewsOutput


def search_news_node(
    state: SearchNewsInput,
    config: RunnableConfig,
    runtime: Runtime[Context]
) -> SearchNewsOutput:
    """
    title: AI新闻搜索
    desc: 搜索最近一天的AI领域最新新闻，筛选出10条高质量内容
    integrations: web-search
    """
    ctx = new_context(method="search.ai_news")
    client = SearchClient(ctx=ctx)

    response = client.search(
        query="AI product launch ChatGPT Gemini AI app case study gaming application implementation",
        search_type="web",
        count=15,
        need_url=True,
        time_range="1d",
        need_summary=True
    )

    news_list = []
    if response.web_items:
        for item in response.web_items[:10]:
            news_list.append({
                "title": item.title or "",
                "url": item.url or "",
                "site_name": item.site_name or "",
                "snippet": item.snippet or "",
                "summary": item.summary or ""
            })

    return SearchNewsOutput(news_list=news_list)
