"""
飞书消息推送节点
"""
import json
import requests
from langchain_core.runnables import RunnableConfig
from langgraph.runtime import Runtime
from coze_coding_utils.runtime_ctx.context import Context
from coze_workload_identity import Client

from graphs.state import SendNotificationInput, SendNotificationOutput


def send_notification_node(
    state: SendNotificationInput,
    config: RunnableConfig,
    runtime: Runtime[Context]
) -> SendNotificationOutput:
    """
    title: 飞书消息推送
    desc: 将格式化后的新闻内容通过飞书机器人推送给用户
    integrations: feishu-message
    """
    try:
        client = Client()
        credential = client.get_integration_credential("integration-feishu-message")
        webhook_info = json.loads(credential)
        webhook_url = webhook_info.get("webhook_url", "")

        if not webhook_url:
            return SendNotificationOutput(send_result="❌ 未配置飞书webhook地址")

        # 拼接新闻和行业总结
        summary_block = ""
        if state.news_summary:
            summary_block = "\n---\n\n" + state.news_summary
        
        full_content = state.formatted_news + summary_block
        
        # 飞书限制每个文本块4000字符，分块发送确保总结完整
        if len(full_content) <= 4000:
            content_blocks = [[{"tag": "text", "text": full_content}]]
        else:
            # 第一个块放新闻（留500字符给总结前缀）
            news_block = state.formatted_news[:3500]
            # 第二个块完整放总结
            summary_text = summary_block if summary_block else ""
            if summary_text:
                content_blocks = [
                    [{"tag": "text", "text": news_block}],
                    [{"tag": "text", "text": summary_text}]
                ]
            else:
                content_blocks = [[{"tag": "text", "text": state.formatted_news[:4000]}]]

        payload = {
            "msg_type": "post",
            "content": {
                "post": {
                    "zh_cn": {
                        "title": "🤖 AI 每日新闻速递",
                        "content": content_blocks
                    }
                }
            }
        }

        response = requests.post(webhook_url, json=payload, timeout=10)
        result = response.json()

        if result.get("code") == 0 or result.get("StatusCode") == 0:
            return SendNotificationOutput(send_result="✅ 飞书消息发送成功")
        else:
            return SendNotificationOutput(send_result=f"❌ 发送失败: {result.get('msg', '未知错误')}")

    except Exception as e:
        return SendNotificationOutput(send_result=f"❌ 发送异常: {str(e)}")
