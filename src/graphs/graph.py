"""
AI新闻订阅工作流主图编排
"""
from langgraph.graph import StateGraph, END

from graphs.state import (
    GlobalState,
    GraphInput,
    GraphOutput,
)
from graphs.nodes.search_news_node import search_news_node
from graphs.nodes.format_news_node import format_news_node
from graphs.nodes.send_notification_node import send_notification_node


builder = StateGraph(GlobalState, input_schema=GraphInput, output_schema=GraphOutput)

builder.add_node("search_news", search_news_node)
builder.add_node("format_news", format_news_node)
builder.add_node("send_notification", send_notification_node)

builder.set_entry_point("search_news")
builder.add_edge("search_news", "format_news")
builder.add_edge("format_news", "send_notification")
builder.add_edge("send_notification", END)

main_graph = builder.compile()
