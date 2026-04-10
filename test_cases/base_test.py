import unittest
import pytest
import allure
from common.request import request
from common.log import log
from common.case_relation import case_relation
from push.push_manager import push_manager

class BaseTest:
    def setup_method(self):
        log.info("Test case setup")
    
    def teardown_method(self):
        log.info("Test case teardown")
    
    def send_request(self, method, url, **kwargs):
        method = method.lower()
        log.info(f"Sending {method} request to {url}")
        log.info(f"Request data: {kwargs}")
        
        # 移除不支持的参数
        if method in ['get', 'delete']:
            # GET和DELETE方法不支持json参数
            kwargs.pop('json', None)
        
        if method == 'get':
            response = request.get(url, **kwargs)
        elif method == 'post':
            response = request.post(url, **kwargs)
        elif method == 'put':
            response = request.put(url, **kwargs)
        elif method == 'delete':
            response = request.delete(url, **kwargs)
        else:
            raise ValueError(f"Unsupported method: {method}")
        
        log.info(f"Response status code: {response.status_code}")
        log.info(f"Response content: {response.text}")
        return response
    
    def extract_variable(self, key, value):
        case_relation.set_variable(key, value)
        log.info(f"Extracted variable: {key} = {value}")
    
    def get_variable(self, key, default=None):
        return case_relation.get_variable(key, default)

class UnittestBaseTest(unittest.TestCase, BaseTest):
    def setUp(self):
        self.setup_method()
    
    def tearDown(self):
        self.teardown_method()

class PytestBaseTest(BaseTest):
    pass
