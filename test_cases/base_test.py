# -*- coding: utf-8 -*-
# -----------------------------
# @Author    : 影子
# @Time      : 2025/3/12 15:31
# @Software  : PyCharm
# @FileName  : base_test.py
# -----------------------------
import unittest
import pytest
import allure
from common.request import request
from common.log import log
from common.case_relation import case_relation
from push.push_manager import push_manager

class BaseTest:
    """
    测试基类，包含测试用例的初始化和清理方法
    """
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
        """
        提取并存储测试用例中的变量值

        :param key: 变量名称，用于标识和后续引用该变量
        :param value: 变量值，需要存储的具体数据
        :return: None
        """
        case_relation.set_variable(key, value)
        log.info(f"Extracted variable: {key} = {value}")

    def get_variable(self, key, default=None):
        """
        获取已存储的测试用例变量值

        :param key: 变量名称，用于查找对应的变量值
        :param default: 默认值，当变量不存在时返回此值，默认为None
        :return: 变量值，如果变量存在则返回其值，否则返回default参数指定的默认值
        """
        return case_relation.get_variable(key, default)

class UnittestBaseTest(unittest.TestCase, BaseTest):
    """
    基于unittest框架的测试基类
    继承自unittest.TestCase和BaseTest，提供unittest风格的测试生命周期管理
    适用于使用unittest框架编写的测试用例
    """

    def setUp(self):
        """
        unittest测试用例执行前的初始化方法
        调用setup_method进行测试环境的准备工作
        """
        self.setup_method()

    def tearDown(self):
        """
        unittest测试用例执行后的清理方法
        调用teardown_method进行测试环境的清理工作
        """
        self.teardown_method()

class PytestBaseTest(BaseTest):
    """
    基于pytest框架的测试基类
    继承自BaseTest，专为pytest框架设计的测试基类
    适用于使用pytest框架编写的测试用例，利用pytest的fixture机制进行管理
    """
    pass

