from config.config import config
from push.email import email_push
from push.dingtalk import dingtalk_push
from push.feishu import feishu_push
from push.wecom import wecom_push
from common.log import log

class PushManager:
    def __init__(self):
        self.push_config = config.get('push', {})
    
    def send_notification(self, subject, content):
        if self.push_config.get('email', False):
            email_push.send(subject, content)
        
        if self.push_config.get('dingtalk', False):
            dingtalk_push.send(f"{subject}\n\n{content}")
        
        if self.push_config.get('feishu', False):
            feishu_push.send(f"{subject}\n\n{content}")
        
        if self.push_config.get('wecom', False):
            wecom_push.send(f"{subject}\n\n{content}")

push_manager = PushManager()
