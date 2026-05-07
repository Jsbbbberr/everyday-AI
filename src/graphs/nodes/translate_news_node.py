"""
翻译新闻节点 - 将英文/韩语新闻翻译成中文
"""
import json
import logging
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.runnables import RunnableConfig
from langgraph.runtime import Runtime
from coze_coding_utils.runtime_ctx.context import Context
from coze_coding_dev_sdk import LLMClient

from graphs.state import TranslateNewsInput, TranslateNewsOutput

logger = logging.getLogger(__name__)


def translate_news_node(
    state: TranslateNewsInput,
    config: RunnableConfig,
    runtime: Runtime[Context]
) -> TranslateNewsOutput:
    """
    title: 翻译新闻
    desc: 将英文/韩语新闻标题和摘要翻译成中文
    integrations: 大语言模型
    """
    ctx = runtime.context
    news_list = state.news_list

    if not news_list:
        return TranslateNewsOutput(translated_news_list=[])

    # 构建翻译提示
    news_text = "\n\n".join([
        f"标题: {item.get('title', '')}\n摘要: {item.get('description', item.get('snippet', ''))}"
        for item in news_list
    ])

    prompt = f"""请将以下新闻的标题和摘要翻译成中文。只翻译标题和摘要部分，保留原文格式。

{news_text}

请以JSON格式返回，格式如下（每条新闻必须有title_cn和description_cn字段）：
[
  {{"title_cn": "中文标题", "description_cn": "中文摘要"}},
  ...
]"""

    try:
        client = LLMClient(ctx=ctx)
        messages = [
            SystemMessage(content="你是一个专业的AI新闻翻译专家，将英文和韩语翻译成中文。"),
            HumanMessage(content=prompt)
        ]
        
        response = client.invoke(messages=messages, temperature=0.3)
        
        # 解析响应
        content = response.content
        if isinstance(content, str):
            translated_text = content.strip()
        elif isinstance(content, list):
            translated_text = " ".join([
                item.get("text", "") if isinstance(item, dict) else str(item)
                for item in content
            ])
        else:
            translated_text = str(content)
        
        # 提取JSON
        json_start = translated_text.find("[")
        json_end = translated_text.rfind("]") + 1
        if json_start != -1 and json_end > json_start:
            json_str = translated_text[json_start:json_end]
            translations = json.loads(json_str)
        else:
            translations = []
        
        # 合并翻译结果
        translated_news_list = []
        for i, item in enumerate(news_list):
            translation = translations[i] if i < len(translations) else {}
            translated_item = {
                "title": item.get("title", ""),
                "title_cn": translation.get("title_cn", item.get("title", "")),
                "url": item.get("url", ""),
                "source": item.get("source", ""),
                "description": item.get("description", item.get("snippet", "")),
                "description_cn": translation.get("description_cn", item.get("description", item.get("snippet", "")))
            }
            translated_news_list.append(translated_item)
        
        logger.info(f"翻译了 {len(translated_news_list)} 条新闻")
        return TranslateNewsOutput(translated_news_list=translated_news_list)
        
    except Exception as e:
        logger.error(f"翻译失败: {e}")
        # 翻译失败时使用原文
        translated_news_list = [
            {
                "title": item.get("title", ""),
                "title_cn": item.get("title", ""),
                "url": item.get("url", ""),
                "source": item.get("source", ""),
                "description": item.get("description", item.get("snippet", "")),
                "description_cn": item.get("description", item.get("snippet", ""))
            }
            for item in news_list
        ]
        return TranslateNewsOutput(translated_news_list=translated_news_list)
