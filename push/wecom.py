import httpx
from config.config import config
from common.log import log

class WeComPush:
    def __init__(self):
        self.webhook = config.get('wecom.webhook')
    
    def send(self, content):
        if not self.webhook:
            log.warning("WeCom webhook is not configured")
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
                log.info("WeCom message sent successfully")
                return True
            else:
                log.error(f"Failed to send WeCom message: {result.get('errmsg')}")
                return False
        except Exception as e:
            log.error(f"Failed to send WeCom message: {str(e)}")
            return False

wecom_push = WeComPush()
