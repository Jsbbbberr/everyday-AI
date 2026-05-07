#!/usr/bin/env python3
"""
定时调用 Coze 工作流 API
使用方式：
  python call_workflow_api.py

或配合 cron：
  0 10 * * * /path/to/python /path/to/call_workflow_api.py
"""
import requests
import json
import logging

# TODO: 替换为你的工作流 API 地址（部署后在 Coze 平台获取）
WORKFLOW_API_URL = "https://your-workflow-api-url"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def run_workflow():
    """调用工作流 API"""
    try:
        logger.info("开始执行工作流...")
        
        response = requests.post(
            WORKFLOW_API_URL,
            json={},
            headers={"Content-Type": "application/json"},
            timeout=60
        )
        
        result = response.json()
        logger.info(f"工作流执行结果: {result}")
        
        return result
    except Exception as e:
        logger.error(f"工作流调用失败: {e}")
        raise


if __name__ == "__main__":
    run_workflow()
