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
from common.mock import mock_server


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
        log.info(f"向{url}发送{method}请求")
        log.info(f"请求数据: {kwargs}")

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

        log.info(f"响应状态: {response.status_code}")
        log.info(f"响应内容：{response.text}")
        return response

    def extract_variable(self, key, value):
        """
        提取并存储测试用例中的变量值

        :param key: 变量名称，用于标识和后续引用该变量
        :param value: 变量值，需要存储的具体数据
        :return: None
        """
        case_relation.set_variable(key, value)
        log.info(f"提取的变量：{key} = {value}")

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
    
    Mock 服务管理：
    - 默认启动 Mock 服务器（类级别）
    - 如果不需要 Mock，可以设置 _enable_mock = False
    """
    
    # 是否启用 Mock 服务，默认为 True
    # 如果测试类不需要 Mock，可以在子类中设置为 False
    _enable_mock = True
    _mock_server_started = False

    @classmethod
    def setUpClass(cls):
        """
        unittest类级别初始化，启动Mock服务器（只启动一次）
        如果 _enable_mock = False，则跳过 Mock 服务器启动
        """
        if cls._enable_mock and not cls._mock_server_started:
            log.info("Unittest: 启动 Mock 服务器")
            mock_server.start()
            cls._mock_server_started = True
        elif not cls._enable_mock:
            log.info(f"Unittest: {cls.__name__} 禁用 Mock 服务")

    @classmethod
    def tearDownClass(cls):
        """
        unittest类级别清理，停止Mock服务器
        """
        if cls._enable_mock and cls._mock_server_started:
            log.info("Unittest: 停止 Mock 服务器")
            mock_server.stop()
            mock_server.clear_mock_responses()
            cls._mock_server_started = False

    def setUp(self):
        """
        unittest测试用例执行前的初始化方法
        调用setup_method进行测试环境的准备工作
        """
        self.setup_method()

    def tearDown(self):
        """
        unittest测试用例执行后的清理方法
        如果启用了 Mock，清理Mock配置，确保用例之间互不影响
        """
        if self._enable_mock:
            mock_server.clear_mock_responses()
        self.teardown_method()


class PytestBaseTest(BaseTest):
    """
    基于pytest框架的测试基类
    继承自BaseTest，专为pytest框架设计的测试基类
    适用于使用pytest框架编写的测试用例，利用pytest的fixture机制进行管理
    
    Mock 服务管理：
    - 默认启动 Mock 服务器（类级别）
    - 如果不需要 Mock，可以设置 _enable_mock = False
    """
    
    # 是否启用 Mock 服务，默认为 True
    # 如果测试类不需要 Mock，可以在子类中设置为 False
    _enable_mock = True

    @pytest.fixture(scope='class', autouse=True)
    def mock_server_class(self, request):
        """
        类级别的 Mock 服务器管理
        每个测试类启动/停止一次 Mock 服务器
        如果 _enable_mock = False，则跳过 Mock 服务器启动
        """
        cls = request.cls
        if cls and hasattr(cls, '_enable_mock') and cls._enable_mock:
            log.info("Pytest: 启动 Mock 服务器")
            mock_server.start()
            yield
            log.info("Pytest: 停止 Mock 服务器")
            mock_server.stop()
            mock_server.clear_mock_responses()
        else:
            if cls:
                log.info(f"Pytest: {cls.__name__} 禁用 Mock 服务")
            yield

    @pytest.fixture(autouse=True)
    def clear_mock_after_test(self, request):
        """
        每个测试用例执行后清理 Mock 配置
        确保用例之间互不影响（仅在启用 Mock 时）
        """
        yield
        cls = request.cls
        if cls and hasattr(cls, '_enable_mock') and cls._enable_mock:
            mock_server.clear_mock_responses()



