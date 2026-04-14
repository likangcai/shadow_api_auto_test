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
from push.template_manager import template_manager

class WeComPush:
    def __init__(self):
        self.webhook = config.get('wecom.webhook')
    
    def send(self, content=None, variables=None):
        """
        发送企业微信消息
        
        :param content: 直接发送的内容（兼容旧接口）
        :param variables: 变量字典，用于渲染模板
        :return: bool
        """
        if not self.webhook:
            log.warning("企微webhook未配置")
            return False
        
        # 如果提供了 variables，使用模板渲染
        if variables:
            content = template_manager.render('wecom', variables)
        elif not content:
            log.warning("企微消息内容为空")
            return False
        
        try:
            headers = {'Content-Type': 'application/json'}
            data = {
                "msgtype": "markdown",
                "markdown": {
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
