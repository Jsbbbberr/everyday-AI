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

# 扣子工作流 API 地址
WORKFLOW_API_URL = "https://fsszyxc9bk.coze.site/run"

# API Token
API_TOKEN = "eyJhbGciOiJSUzI1NiIsImtpZCI6IjQ0MGI0ZDY0LTM5ODQtNDRjYy05ZjUwLTdjZjkxYjA1NGI3OSJ9.eyJpc3MiOiJodHRwczovL2FwaS5jb3plLmNuIiwiYXVkIjpbIlVwVXJaMDY1UHRDM2xVQmFqS1lRV092Qm5CS1ZseFl4Il0sImV4cCI6ODIxMDI2Njg3Njc5OSwiaWF0IjoxNzc4MTM2MTU2LCJzdWIiOiJzcGlmZmU6Ly9hcGkuY296ZS5jbi93b3JrbG9hZF9pZGVudGl0eS9pZDo3NjM3MDI0NDk1NDA3OTg4NzUxIiwic3JjIjoiaW5ib3VuZF9hdXRoX2FjY2Vzc190b2tlbl9pZDo3NjM3MDM2NjQxNjY3Nzc2NTY0In0.ehElgt32zNP-_OilJWxmdEQftzEzfTkvo24o9F264grmlWTW-yfZUqy7wAHUBrpmiqUX2a6QnPsX31Y2U8eOw93NlcDZoBBU1Npcwgxf_NMkywbxQaTf-Ld_52GAqt8VEDauYrIJO_plpAf3_ubaSjvqryzLbcKXKxR0461P75ylthPCGTrtzpz5DPARCFsVnMN7eEWphkFLX3zw6vLnF1acayoBxPgMZ_Z4JnjkyYMKHcjRqLbiyaLW2O38qnPvL7GXnZKyI_Z2uehm7_BS0HpNfNI2amFM5J_YrNANdRkCQigd2WTFB3AV8IGq9-SAaXEUCbDiH4qBkCmjA2mgiQ"

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
