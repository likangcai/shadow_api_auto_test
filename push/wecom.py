# -*- coding: utf-8 -*-
# -----------------------------
# @Author    : 影子
# @Time      : 2025/3/12 10:43
# @Software  : PyCharm
# @FileName  : wecom.py
# -----------------------------
import httpx
from config.config import config
from common.log import log

class WeComPush:
    def __init__(self):
        self.webhook = config.get('wecom.webhook')
    
    def send(self, content):
        if not self.webhook:
            log.warning("企微webhook未配置")
            return False
        
        try:
            headers = {'Content-Type': 'application/json'}
            data = {
                "msgtype": "text",
                "text": {
                    "content": content
                }
            }
            
            response = httpx.post(self.webhook, json=data, headers=headers)
            result = response.json()
            if result.get('errcode') == 0:
                log.info("企微消息发送成功")
                return True
            else:
                log.error(f"企微消息发送失败: {result.get('errmsg')}")
                return False
        except Exception as e:
            log.error(f"企微消息发送失败: {str(e)}")
            return False

wecom_push = WeComPush()
