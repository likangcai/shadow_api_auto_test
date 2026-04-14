# -*- coding: utf-8 -*-
# -----------------------------
# @Author    : 影子
# @Time      : 2026/4/14 11:30
# @Software  : PyCharm
# @FileName  : test_without_mock.py
# -----------------------------
"""
不使用 Mock 服务的测试用例示例
展示如何编写不需要 Mock 的普通 API 测试
"""
import pytest
import allure
from test_cases.base_test import PytestBaseTest


@allure.feature("真实API测试")
@allure.story("不使用Mock服务")
class TestWithoutMock(PytestBaseTest):
    """
    不需要 Mock 服务的测试用例
    
    注意：虽然继承了 PytestBaseTest，但如果不使用 mock_server，
    Mock 服务器的启动和停止不会对这些测试产生任何影响。
    Mock 服务器会在后台运行，但这些测试直接调用真实 API。
    """

    @allure.title("测试真实的HTTPBin GET请求")
    def test_real_api_get(self):
        """测试真实的 HTTPBin API（不使用 Mock）"""
        # 这个测试直接调用真实的 HTTPBin 服务
        # 不会受到 Mock 服务器的影响
        response = self.send_request('get', 'https://httpbin.org/get')
        
        assert response.status_code == 200
        data = response.json()
        assert 'url' in data
        assert data['url'] == 'https://httpbin.org/get'

    @allure.title("测试真实的HTTPBin POST请求")
    def test_real_api_post(self):
        """测试真实的 HTTPBin API POST 请求"""
        test_data = {
            'name': 'Test User',
            'email': 'test@example.com'
        }
        
        response = self.send_request(
            'post',
            'https://httpbin.org/post',
            json=test_data
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data['json']['name'] == 'Test User'
        assert data['json']['email'] == 'test@example.com'

    @allure.title("测试变量提取和复用")
    def test_variable_extraction(self):
        """测试用例间的变量传递"""
        # 第一个请求：获取数据
        response = self.send_request('get', 'https://httpbin.org/uuid')
        assert response.status_code == 200
        
        uuid = response.json()['uuid']
        self.extract_variable('test_uuid', uuid)
        
        # 第二个请求：使用提取的变量
        stored_uuid = self.get_variable('test_uuid')
        assert stored_uuid == uuid

    @allure.title("测试请求头处理")
    def test_custom_headers(self):
        """测试自定义请求头"""
        headers = {
            'X-Custom-Header': 'test-value',
            'Accept': 'application/json'
        }
        
        response = self.send_request(
            'get',
            'https://httpbin.org/headers',
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert 'X-Custom-Header' in data['headers']


class TestUnittestWithoutMock:
    """
    Unittest 引擎的不使用 Mock 的测试示例
    
    注意：这个类没有继承 UnittestBaseTest，所以完全不会涉及 Mock 服务
    适用于完全不需要 Mock 的简单测试场景
    """

    def test_simple_assertion(self):
        """简单的断言测试"""
        assert 1 + 1 == 2
        assert 'hello'.upper() == 'HELLO'

    def test_list_operations(self):
        """列表操作测试"""
        my_list = [1, 2, 3, 4, 5]
        assert len(my_list) == 5
        assert 3 in my_list
        assert sum(my_list) == 15

    def test_dict_operations(self):
        """字典操作测试"""
        my_dict = {'name': 'Alice', 'age': 30}
        assert my_dict['name'] == 'Alice'
        assert 'age' in my_dict
        assert len(my_dict) == 2


if __name__ == '__main__':
    import unittest
    unittest.main()
