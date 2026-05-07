"""
AI新闻订阅工作流状态定义
"""
from typing import List, Optional
from pydantic import BaseModel, Field


class GlobalState(BaseModel):
    """全局状态定义"""
    news_list: List[dict] = Field(default_factory=list, description="搜索到的新闻列表")
    translated_news_list: List[dict] = Field(default_factory=list, description="翻译后的新闻列表")
    formatted_news: str = Field(default="", description="格式化后的新闻内容")
    news_summary: str = Field(default="", description="行业总结")
    send_result: str = Field(default="", description="发送结果")


class GraphInput(BaseModel):
    """工作流输入"""
    pass


class GraphOutput(BaseModel):
    """工作流输出"""
    formatted_news: str = Field(..., description="格式化后的新闻内容")
    news_summary: str = Field(default="", description="行业总结")
    send_result: str = Field(default="", description="发送结果")


class SearchNewsInput(BaseModel):
    """新闻搜索节点输入"""
    pass


class SearchNewsOutput(BaseModel):
    """新闻搜索节点输出"""
    news_list: List[dict] = Field(..., description="搜索到的新闻列表，包含标题、URL、摘要")


class FormatNewsInput(BaseModel):
    """新闻格式化节点输入"""
    news_list: List[dict] = Field(..., description="搜索到的新闻列表")


class FormatNewsOutput(BaseModel):
    """新闻格式化节点输出"""
    formatted_news: str = Field(..., description="格式化后的新闻内容")


class SendNotificationInput(BaseModel):
    """发送通知节点输入"""
    formatted_news: str = Field(..., description="格式化后的新闻内容")


class SendNotificationOutput(BaseModel):
    """发送通知节点输出"""
    send_result: str = Field(..., description="发送结果")


class TranslateNewsInput(BaseModel):
    """翻译新闻节点输入"""
    news_list: List[dict] = Field(..., description="搜索到的新闻列表，包含标题、URL、摘要")


class TranslateNewsOutput(BaseModel):
    """翻译新闻节点输出"""
    translated_news_list: List[dict] = Field(..., description="翻译后的新闻列表")


class SummaryNewsInput(BaseModel):
    """行业总结节点输入"""
    formatted_news: str = Field(..., description="格式化后的新闻内容")
    news_list: List[dict] = Field(default=[], description="新闻列表")


class SummaryNewsOutput(BaseModel):
    """行业总结节点输出"""
    news_summary: str = Field(..., description="AI生成的行业总结")
