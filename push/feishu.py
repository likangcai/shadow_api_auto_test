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
from push.template_manager import template_manager

class FeiShuPush:
    def __init__(self):
        self.webhook = config.get('feishu.webhook')
    
    def send(self, content=None, variables=None):
        """
        发送飞书消息
        
        :param content: 直接发送的内容（兼容旧接口）
        :param variables: 变量字典，用于渲染模板
        :return: bool
        """
        if not self.webhook:
            log.warning("未配置飞书webhook")
            return False
        
        # 如果提供了 variables，使用模板渲染
        if variables:
            content = template_manager.render('feishu', variables)
        elif not content:
            log.warning("飞书消息内容为空")
            return False
        
        try:
            headers = {'Content-Type': 'application/json'}
            data = {
                "msg_type": "post",
                "content": {
                    "post": {
                        "zh_cn": {
                            "title": variables.get('title', '测试报告') if variables else '测试报告',
                            "content": [
                                [
                                    {
                                        "tag": "text",
                                        "text": content
                                    }
                                ]
                            ]
                        }
                    }
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
