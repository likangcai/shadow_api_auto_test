import httpx
import time
import hmac
import hashlib
import base64
from config.config import config
from common.log import log

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
    
    def send(self, content):
        if not self.webhook:
            log.warning("DingTalk webhook is not configured")
            return False
        
        try:
            headers = {'Content-Type': 'application/json'}
            data = {
                "msgtype": "text",
                "text": {
                    "content": content
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
                log.info("DingTalk message sent successfully")
                return True
            else:
                log.error(f"Failed to send DingTalk message: {result.get('errmsg')}")
                return False
        except Exception as e:
            log.error(f"Failed to send DingTalk message: {str(e)}")
            return False

dingtalk_push = DingTalkPush()
