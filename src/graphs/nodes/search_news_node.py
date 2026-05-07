"""
AI新闻搜索节点 - 使用 GDELT API
"""
import requests
from datetime import datetime
from langchain_core.runnables import RunnableConfig
from langgraph.runtime import Runtime
from coze_coding_utils.runtime_ctx.context import Context

from graphs.state import SearchNewsInput, SearchNewsOutput


def search_news_node(
    state: SearchNewsInput,
    config: RunnableConfig,
    runtime: Runtime[Context]
) -> SearchNewsOutput:
    """
    title: AI新闻搜索
    desc: 使用GDELT API搜索全球AI领域最新新闻，重点关注海外产品发布和实际应用案例
    integrations: 
    """
    # GDELT DOC 2.0 API - 搜索最近24小时的AI新闻
    base_url = "https://api.gdeltproject.org/api/v2/doc/doc"
    
    # 英文AI新闻关键词组合
    search_queries = [
        '"ChatGPT" OR "Gemini" OR "Claude" AI product',  # AI产品发布
        '"artificial intelligence" app launch gaming',      # AI应用游戏
        '"AI" "machine learning" case study implementation', # 实际案例
    ]
    
    all_articles = []
    
    for query in search_queries:
        try:
            params = {
                "query": query,
                "mode": "artlist",
                "maxrecords": 30,
                "format": "json",
                "sort": "Date DESC",
                "sourcecountry": "US,GB"  # 只搜索美国和英国的新闻
            }
            
            response = requests.get(base_url, params=params, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                if "articles" in data:
                    for article in data["articles"]:
                        # 只保留英文内容
                        language = article.get("language", "")
                        if language == "English" or not language:
                            all_articles.append(article)
        except Exception:
            continue
    
    # 去重
    seen_urls = set()
    unique_articles = []
    for article in all_articles:
        url = article.get("url", "")
        if url and url not in seen_urls:
            seen_urls.add(url)
            unique_articles.append(article)
    
    # 过滤低质量来源并取前10条
    exclude_domains = ["twitter.com", "facebook.com", "reddit.com", 
                      "youtube.com", "tiktok.com", "instagram.com",
                      "weibo.com", "toutiao.com", "baidu.com", "naver.com",
                      "kakao.com", "qq.com"]
    
    news_list = []
    for article in unique_articles:
        url = article.get("url", "")
        domain = article.get("domain", "").lower()
        
        # 排除低质量来源
        if any(ex in domain for ex in exclude_domains):
            continue
        
        title = article.get("title", "")
        if not title or len(title) < 15:
            continue
        
        news_list.append({
            "title": title.strip(),
            "url": url,
            "site_name": article.get("domain", ""),
            "snippet": article.get("text", "")[:200] if article.get("text") else "",
            "summary": article.get("text", "")[:300] if article.get("text") else ""
        })
        
        if len(news_list) >= 10:
            break
    
    return SearchNewsOutput(news_list=news_list)
