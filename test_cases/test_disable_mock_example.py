# -*- coding: utf-8 -*-
# -----------------------------
# @Author    : 影子
# @Time      : 2026/4/14 11:45
# @Software  : PyCharm
# @FileName  : test_disable_mock_example.py
# -----------------------------
"""
禁用 Mock 服务的测试用例示例
展示如何在继承基类的情况下禁用 Mock 服务
"""
import pytest
import allure
from test_cases.base_test import PytestBaseTest, UnittestBaseTest


@allure.feature("禁用Mock示例")
@allure.story("Pytest引擎禁用Mock")
class TestPytestDisableMock(PytestBaseTest):
    """
    Pytest 引擎禁用 Mock 服务的示例
    
    通过设置 _enable_mock = False，可以禁用 Mock 服务器
    适用于需要调用真实 API 的测试场景
    """
    
    # 禁用 Mock 服务
    _enable_mock = False

    @allure.title("测试真实API - 禁用Mock后调用真实服务")
    def test_real_api_call(self):
        """
        这个测试会调用真实的 HTTPBin API
        因为 _enable_mock = False，Mock 服务器不会启动
        """
        response = self.send_request('get', 'https://httpbin.org/get')
        
        assert response.status_code == 200
        data = response.json()
        assert 'url' in data
        assert data['url'] == 'https://httpbin.org/get'

    @allure.title("测试真实POST请求")
    def test_real_post_request(self):
        """测试真实的 POST 请求"""
        test_data = {'name': 'Real User', 'email': 'real@example.com'}
        
        response = self.send_request(
            'post',
            'https://httpbin.org/post',
            json=test_data
        )
        
        assert response.status_code == 200
        assert response.json()['json']['name'] == 'Real User'


class TestPytestEnableMock(PytestBaseTest):
    """
    Pytest 引擎启用 Mock 服务的示例（默认行为）
    
    这个类会使用 Mock 服务器，与上一个类形成对比
    """
    
    # 显式启用 Mock 服务（其实这是默认值）
    _enable_mock = True

    def test_with_mock_server(self):
        """这个测试会使用 Mock 服务器"""
        from common.mock import mock_server
        
        mock_server.set_mock_response('/api/test', {
            'status_code': 200,
            'body': {'message': 'Mocked response'}
        })
        
        import httpx
        response = httpx.get('http://localhost:8888/api/test')
        
        assert response.status_code == 200
        assert response.json()['message'] == 'Mocked response'


# ==================== Unittest 引擎示例 ====================

import unittest


class TestUnittestDisableMock(UnittestBaseTest):
    """
    Unittest 引擎禁用 Mock 服务的示例
    
    通过设置 _enable_mock = False，可以禁用 Mock 服务器
    """
    
    # 禁用 Mock 服务
    _enable_mock = False

    def test_real_api_without_mock(self):
        """
        这个测试会调用真实的 HTTPBin API
        因为 _enable_mock = False，Mock 服务器不会启动
        """
        response = self.send_request('get', 'https://httpbin.org/get')
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('url', data)
        self.assertEqual(data['url'], 'https://httpbin.org/get')

    def test_another_real_api_call(self):
        """另一个真实 API 测试"""
        response = self.send_request('get', 'https://httpbin.org/uuid')
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('uuid', response.json())


class TestUnittestEnableMock(UnittestBaseTest):
    """
    Unittest 引擎启用 Mock 服务的示例（默认行为）
    """
    
    # 显式启用 Mock 服务
    _enable_mock = True

    def test_with_mock_enabled(self):
        """这个测试会使用 Mock 服务器"""
        from common.mock import mock_server
        import httpx
        
        mock_server.set_mock_response('/api/mock-test', {
            'status_code': 200,
            'body': {'status': 'mocked'}
        })
        
        response = httpx.get('http://localhost:8888/api/mock-test')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'mocked')


if __name__ == '__main__':
    unittest.main()
