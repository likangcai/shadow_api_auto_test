import httpx
import time
from config.config import config
from common.log import log

class Request:
    def __init__(self):
        self.base_url = config.get('base_url')
        self.timeout = config.get('timeout', 30)
        self.verify_ssl = config.get('verify_ssl', False)
        self.retry_count = config.get('retry_count', 3)
        self.retry_interval = config.get('retry_interval', 1)
        self.session = httpx.Client(
            base_url=self.base_url,
            timeout=self.timeout,
            verify=self.verify_ssl
        )
    
    def _request(self, method, url, **kwargs):
        for i in range(self.retry_count):
            try:
                response = getattr(self.session, method)(url, **kwargs)
                return response
            except Exception as e:
                log.warning(f"Request failed (attempt {i+1}/{self.retry_count}): {str(e)}")
                if i < self.retry_count - 1:
                    time.sleep(self.retry_interval)
                else:
                    raise
    
    def get(self, url, params=None, headers=None, **kwargs):
        return self._request('get', url, params=params, headers=headers, **kwargs)
    
    def post(self, url, json=None, data=None, headers=None, **kwargs):
        return self._request('post', url, json=json, data=data, headers=headers, **kwargs)
    
    def put(self, url, json=None, data=None, headers=None, **kwargs):
        return self._request('put', url, json=json, data=data, headers=headers, **kwargs)
    
    def delete(self, url, headers=None, **kwargs):
        return self._request('delete', url, headers=headers, **kwargs)
    
    def close(self):
        self.session.close()

request = Request()
