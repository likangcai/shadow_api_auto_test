# -*- coding: utf-8 -*-
# -----------------------------
# @Author    : 影子
# @Time      : 2025/3/12 09:08
# @Software  : PyCharm
# @FileName  : dingtalk.py
# -----------------------------
import httpx
import time
import hmac
import hashlib
import base64
from config.config import config
from common.log import log
from push.template_manager import template_manager

class DingTalkPush:
    def __init__(self):
        self.webhook = config.get('dingtalk.webhook')
        self.secret = config.get('dingtalk.secret')
    
    def _get_sign(self):
        timestamp = str(round(time.time() * 1000))
        secret_enc = self.secret.encode('utf-8')
        string_to_sign = f'{timestamp}\n{self.secret}'
        string_to_sign_enc = string_to_sign.encode('utf-8')
        hmac_code = hmac.new(secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
        sign = base64.b64encode(hmac_code).decode('utf-8')
        return timestamp, sign
    
    def send(self, content=None, variables=None):
        """
        发送钉钉消息
        
        :param content: 直接发送的内容（兼容旧接口）
        :param variables: 变量字典，用于渲染模板
        :return: bool
        """
        if not self.webhook:
            log.warning("钉钉webhook未配置")
            return False
        
        # 如果提供了 variables，使用模板渲染
        if variables:
            content = template_manager.render('dingtalk', variables)
        elif not content:
            log.warning("钉钉消息内容为空")
            return False
        
        try:
            headers = {'Content-Type': 'application/json'}
            data = {
                "msgtype": "markdown",
                "markdown": {
                    "title": f"📊 {variables.get('title', '测试报告') if variables else '测试报告'}",
                    "text": content
                }
            }
            
            if self.secret:
                timestamp, sign = self._get_sign()
                webhook_url = f"{self.webhook}&timestamp={timestamp}&sign={sign}"
            else:
                webhook_url = self.webhook
            
            response = httpx.post(webhook_url, json=data, headers=headers)
            result = response.json()
            if result.get('errcode') == 0:
                log.info("钉钉消息发送成功")
                return True
            else:
                log.error(f"发送钉钉消息失败: {result.get('errmsg')}")
                return False
        except Exception as e:
            log.error(f"发送钉钉消息失败: {str(e)}")
            return False

dingtalk_push = DingTalkPush()
