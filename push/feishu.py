import httpx
from config.config import config
from common.log import log

class FeiShuPush:
    def __init__(self):
        self.webhook = config.get('feishu.webhook')
    
    def send(self, content):
        if not self.webhook:
            log.warning("FeiShu webhook is not configured")
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
                log.info("FeiShu message sent successfully")
                return True
            else:
                log.error(f"Failed to send FeiShu message: {result.get('msg')}")
                return False
        except Exception as e:
            log.error(f"Failed to send FeiShu message: {str(e)}")
            return False

feishu_push = FeiShuPush()
