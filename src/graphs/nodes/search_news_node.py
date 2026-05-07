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
        "AI产品发布 2026",
        "ChatGPT Gemini Claude 最新",
        "AI游戏应用案例",
        "AI智能体 agent 最新",
        "AI mobile app launch 2026",
        "OpenAI Anthropic Google update",
        "人工智能 最新动态",
        "大模型 更新 发布",
    ]

    all_news = []
    seen_urls = set()
    seen_titles = set()
    
    # 只保留本周/当日新闻（3天）
    cutoff_days = 3

    def is_similar_title(t1: str, t2: str) -> bool:
        """检查两个标题是否相似"""
        t1, t2 = t1.lower(), t2.lower()
        if t1 == t2 or t1 in t2 or t2 in t1:
            return True
        return False

    def extract_date_from_text(text: str) -> str:
        """从文本中提取日期"""
        import re
        # 匹配各种日期格式
        patterns = [
            r'20\d{2}年\d{1,2}月\d{1,2}日',
            r'20\d{2}[-/]\d{1,2}[-/]\d{1,2}',
        ]
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                date_str = match.group().replace('年', '-').replace('月', '-').replace('日', '').replace('/', '-')
                return date_str
        return ""

    def is_recent_news(publish_time: str = "", description: str = "", url: str = "") -> bool:
        """检查新闻是否是近3天发布的，优先使用URL中的日期"""
        # 优先从URL中提取日期（最可靠）
        date_str = extract_date_from_text(url)
        if not date_str:
            date_str = extract_date_from_text(description)
        if not date_str:
            date_str = extract_date_from_text(publish_time)
        
        if not date_str:
            # GDELT已用time_range="3d"过滤，这里只做额外验证
            # 如果publish_time有日期则验证，否则默认允许
            pub_ts = publish_time.strip() if publish_time else ""
            if pub_ts and len(pub_ts) >= 10:
                try:
                    pub_date = datetime.fromtimestamp(int(pub_ts))
                    days_diff = (datetime.now() - pub_date).days
                    return days_diff <= cutoff_days
                except:
                    pass
            return True  # 无法判断时保留（信任GDELT的time_range过滤）
        
        try:
            pub_date = datetime.strptime(date_str[:10], '%Y-%m-%d')
            days_diff = (datetime.now() - pub_date).days
            return days_diff <= cutoff_days
        except:
            return True

    for query in search_queries:
        try:
            response = client.search(
                query=query,
                search_type="web",
                count=30,  # 增加每次搜索数量
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
                    
                    # 发布时间
                    publish_time = item.publish_time or ""
                    
                    # 描述摘要
                    description = item.summary or item.snippet or ""
                    
                    # 判断语言
                    is_english = not any('\u4e00' <= c <= '\u9fff' for c in title)
                    
                    news_item = {
                        "title": title or '无标题',
                        "url": url,
                        "source": source,
                        "description": description,
                        "publish_time": publish_time,
                        "language": "en" if is_english else "zh"
                    }
                    all_news.append(news_item)
        except Exception as e:
            logger.warning(f"搜索 '{query}' 失败: {e}")
            continue

    # 过滤7天内的新闻
    filtered_news = []
    for news in all_news:
        if is_recent_news(news.get("publish_time", ""), news.get("description", ""), news.get("url", "")):
            filtered_news.append(news)
    
    news_list = filtered_news

    logger.info(f"搜索到 {len(news_list)} 条本周/当日新闻")
    return SearchNewsOutput(news_list=news_list)
