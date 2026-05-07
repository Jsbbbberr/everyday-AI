"""
AI新闻搜索节点 - 使用火山引擎搜索
"""
import logging
from langchain_core.runnables import RunnableConfig
from langgraph.runtime import Runtime
from coze_coding_utils.runtime_ctx.context import Context
from coze_coding_dev_sdk import SearchClient

from graphs.state import SearchNewsInput, SearchNewsOutput

logger = logging.getLogger(__name__)


def search_news_node(
    state: SearchNewsInput,
    config: RunnableConfig,
    runtime: Runtime[Context]
) -> SearchNewsOutput:
    """
    title: AI新闻搜索
    desc: 使用火山引擎搜索AI领域最新新闻，重点关注海外产品发布和实际应用案例
    integrations: web-search
    """
    ctx = runtime.context
    client = SearchClient(ctx=ctx)

    # 搜索海外AI产品和应用案例（中文关键词搜索，国内媒体会转载海外内容）
    search_queries = [
        "AI artificial intelligence product launch app",  # AI产品发布
        "ChatGPT Gemini Claude Anthropic OpenAI",          # 海外AI产品
        "AI machine learning gaming app implementation",   # AI应用游戏
        "artificial intelligence technology breakthrough", # AI技术突破
    ]

    all_news = []
    seen_urls = set()

    for query in search_queries:
        try:
            response = client.search(
                query=query,
                search_type="web",
                count=15,
                need_url=True,
                time_range="7d",
                need_summary=True
            )
            
            if response and response.web_items:
                for item in response.web_items:
                    url = item.url or ''
                    if url and url not in seen_urls:
                        seen_urls.add(url)
                        
                        # 来源
                        source = item.site_name or item.auth_info_des or ""
                        
                        news_item = {
                            "title": item.title or '无标题',
                            "url": url,
                            "source": source,
                            "description": item.summary or item.snippet or "",
                            "language": "en"  # 标记需要翻译
                        }
                        all_news.append(news_item)
        except Exception as e:
            logger.warning(f"搜索 '{query}' 失败: {e}")
            continue

    # 按时间排序并去重
    news_list = all_news[:10]  # 取前10条

    logger.info(f"搜索到 {len(news_list)} 条新闻")
    return SearchNewsOutput(news_list=news_list)
