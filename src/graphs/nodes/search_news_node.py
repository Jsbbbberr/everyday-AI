"""
AI新闻搜索节点 - 使用火山引擎搜索，只抓取近3天新闻
"""
import logging
from datetime import datetime, timedelta
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
    desc: 使用火山引擎搜索AI领域最新新闻，只抓取近3天内容
    integrations: web-search
    """
    ctx = runtime.context
    client = SearchClient(ctx=ctx)

    # 时间范围设置 - 3天
    time_range = "3d"
    
    # 搜索多个不同主题
    search_queries = [
        "AI产品发布",
        "ChatGPT Gemini Claude更新",
        "AI游戏应用",
        "AI智能体应用",
        "AI mobile app launch",
        "OpenAI Anthropic Google update",
    ]

    all_news = []
    seen_urls = set()
    seen_titles = set()
    
    # 只保留3天内的新闻
    cutoff_days = 3

    def is_similar_title(t1: str, t2: str) -> bool:
        """检查两个标题是否相似"""
        t1, t2 = t1.lower(), t2.lower()
        if t1 == t2 or t1 in t2 or t2 in t1:
            return True
        return False

    def is_recent_news(publish_time: str) -> bool:
        """检查新闻是否是近3天发布的"""
        if not publish_time:
            return True
        try:
            pub_date = datetime.strptime(publish_time[:10], '%Y-%m-%d')
            days_diff = (datetime.now() - pub_date).days
            return days_diff <= cutoff_days
        except:
            return True

    for query in search_queries:
        try:
            response = client.search(
                query=query,
                search_type="web",
                count=15,  # 每次多取一些
                need_url=True,
                time_range=time_range,
                need_summary=True
            )
            
            if response and response.web_items:
                for item in response.web_items:
                    url = item.url or ''
                    title = (item.title or '').strip()
                    
                    if not url:
                        continue
                    
                    # URL去重
                    if url in seen_urls:
                        continue
                    seen_urls.add(url)
                    
                    # 标题去重
                    is_dup = False
                    for existing_title in list(seen_titles):
                        if is_similar_title(title, existing_title):
                            is_dup = True
                            break
                    if is_dup:
                        continue
                    seen_titles.add(title)
                    
                    # 来源
                    source = item.site_name or item.auth_info_des or ""
                    
                    # 判断语言
                    is_english = not any('\u4e00' <= c <= '\u9fff' for c in title)
                    
                    news_item = {
                        "title": title or '无标题',
                        "url": url,
                        "source": source,
                        "description": item.summary or item.snippet or "",
                        "language": "en" if is_english else "zh"
                    }
                    all_news.append(news_item)
        except Exception as e:
            logger.warning(f"搜索 '{query}' 失败: {e}")
            continue

    # 不限制数量，直接返回所有结果
    news_list = all_news

    logger.info(f"搜索到 {len(news_list)} 条近3天新闻")
    return SearchNewsOutput(news_list=news_list)
