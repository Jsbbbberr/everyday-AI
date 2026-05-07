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

    # 搜索多个不同主题
    search_queries = [
        "ChatGPT Gemini Claude AI产品发布",  # AI产品
        "AI gaming app implementation",     # 游戏应用
        "AI agent productivity tool",        # 生产力工具
        "OpenAI Anthropic Google AI update", # 海外AI动态
        "AI mobile app launch",              # 移动端应用
        "machine learning practical use case", # 实际案例
    ]

    all_news = []
    seen_urls = set()
    seen_titles = set()  # 用于标题去重

    def is_similar_title(title1: str, title2: str) -> bool:
        """检查两个标题是否相似（用于去重）"""
        t1 = title1.lower()
        t2 = title2.lower()
        # 完全相同
        if t1 == t2:
            return True
        # 一个包含另一个
        if t1 in t2 or t2 in t1:
            return True
        return False

    for query in search_queries:
        try:
            response = client.search(
                query=query,
                search_type="web",
                count=5,  # 每个搜索词只取5条
                need_url=True,
                time_range="7d",
                need_summary=True
            )
            
            if response and response.web_items:
                for item in response.web_items:
                    url = item.url or ''
                    title = (item.title or '').strip()
                    
                    # 必须有URL
                    if not url:
                        continue
                    
                    # URL去重
                    if url in seen_urls:
                        continue
                    seen_urls.add(url)
                    
                    # 标题去重（相似度检查）
                    title_normalized = title.lower()
                    is_duplicate = False
                    for existing_title in seen_titles:
                        if is_similar_title(title_normalized, existing_title):
                            is_duplicate = True
                            break
                    if is_duplicate:
                        continue
                    seen_titles.add(title_normalized)
                    
                    # 来源
                    source = item.site_name or item.auth_info_des or ""
                    
                    news_item = {
                        "title": title or '无标题',
                        "url": url,
                        "source": source,
                        "description": item.summary or item.snippet or "",
                        "language": "en"  # 标记需要翻译
                    }
                    all_news.append(news_item)
        except Exception as e:
            logger.warning(f"搜索 '{query}' 失败: {e}")
            continue

    # 按时间排序并取前10条（已有去重）
    news_list = all_news[:10]  # 取前10条

    logger.info(f"搜索到 {len(news_list)} 条新闻")
    return SearchNewsOutput(news_list=news_list)
