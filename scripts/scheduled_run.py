#!/usr/bin/env python3
"""
定时执行脚本 - AI每日新闻推送
配合 cron 使用: 0 10 * * * /workspace/projects/.venv/bin/python /workspace/projects/scripts/scheduled_run.py
"""
import sys
import os

sys.path.insert(0, "/workspace/projects")

from src.graphs.graph import main_graph
from coze_coding_utils.runtime_ctx.context import new_context
from coze_coding_utils.runtime_ctx.context import Context
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def run_workflow():
    """执行AI新闻推送工作流"""
    try:
        logger.info("开始执行AI新闻推送工作流...")
        
        ctx = new_context(method="scheduled.ai_news")
        result = main_graph.invoke({}, config={"configurable": {"thread_id": ctx.run_id}})
        
        logger.info(f"工作流执行完成: {result.get('send_result', 'unknown')}")
        return result
    except Exception as e:
        logger.error(f"工作流执行失败: {e}")
        raise


if __name__ == "__main__":
    run_workflow()
