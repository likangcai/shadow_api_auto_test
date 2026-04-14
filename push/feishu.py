# -*- coding: utf-8 -*-
# -----------------------------
# @Author    : 影子
# @Time      : 2025/3/12 09:33
# @Software  : PyCharm
# @FileName  : feishu.py
# -----------------------------
import httpx
from config.config import config
from common.log import log

class FeiShuPush:
    def __init__(self):
        self.webhook = config.get('feishu.webhook')
    
    def send(self, content):
        if not self.webhook:
            log.warning("未配置飞书webhook")
            return False
        
        try:
            headers = {'Content-Type': 'application/json'}
            data = {
                "msg_type": "text",
                "content": {
                    "text": content
                }
            }
            
            response = httpx.post(self.webhook, json=data, headers=headers)
            result = response.json()
            if result.get('code') == 0:
                log.info("飞书消息发送成功")
                return True
            else:
                log.error(f"发送飞书消息失败: {result.get('msg')}")
                return False
        except Exception as e:
            log.error(f"发送飞书消息失败: {str(e)}")
            return False

feishu_push = FeiShuPush()
