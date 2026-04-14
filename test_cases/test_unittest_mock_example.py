# -*- coding: utf-8 -*-
# -----------------------------
# @Author    : 影子
# @Time      : 2026/4/14 11:00
# @Software  : PyCharm
# @FileName  : test_unittest_mock_example.py
# -----------------------------
"""
Unittest 引擎的 Mock 服务使用示例
展示如何使用 UnittestBaseTest 进行 API 测试
"""
import unittest
import httpx
from test_cases.base_test import UnittestBaseTest
from common.mock import mock_server, MockResponse


class TestUnittestMockExample(UnittestBaseTest):
    """
    Unittest 引擎的 Mock 测试示例
    继承 UnittestBaseTest 后，Mock 服务器会自动管理
    """

    def test_simple_get_request(self):
        """测试简单的 GET 请求"""
        # 设置 Mock 响应
        mock_server.set_mock_response('/api/users', {
            'status_code': 200,
            'body': {
                'users': [
                    {'id': 1, 'name': 'Alice', 'email': 'alice@example.com'},
                    {'id': 2, 'name': 'Bob', 'email': 'bob@example.com'}
                ]
            }
        })

        # 发起请求
        response = httpx.get('http://localhost:8888/api/users')

        # 验证响应
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data['users']), 2)
        self.assertEqual(data['users'][0]['name'], 'Alice')

    def test_post_with_dynamic_callback(self):
        """测试使用回调函数处理 POST 请求"""

        def create_user_handler(method, headers, body, query_params):
            """动态处理用户创建请求"""
            if not body or not body.get('name'):
                return MockResponse(
                    status_code=400,
                    body={'error': 'Name is required'}
                )

            return MockResponse(
                status_code=201,
                body={
                    'id': 123,
                    'name': body['name'],
                    'email': body.get('email', ''),
                    'created': True
                }
            )

        # 设置动态回调
        mock_server.set_mock_callback('/api/users', create_user_handler)

        # 测试成功场景
        response = httpx.post(
            'http://localhost:8888/api/users',
            json={'name': 'Charlie', 'email': 'charlie@example.com'}
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()['name'], 'Charlie')
        self.assertTrue(response.json()['created'])

        # 测试失败场景（缺少 name）
        response = httpx.post(
            'http://localhost:8888/api/users',
            json={'email': 'noname@example.com'}
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.json())

    def test_get_with_query_params(self):
        """测试带查询参数的 GET 请求"""

        def user_query_handler(method, headers, body, query_params):
            """根据查询参数返回不同用户"""
            user_id = query_params.get('id')
            if user_id:
                return {
                    'user_id': user_id,
                    'name': f'User_{user_id}',
                    'email': f'user{user_id}@example.com'
                }
            return {'error': 'Missing id parameter', 'code': 400}

        mock_server.set_mock_callback('/api/user', user_query_handler)

        # 测试带参数的请求
        response = httpx.get('http://localhost:8888/api/user?id=42')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['user_id'], '42')
        self.assertEqual(response.json()['name'], 'User_42')

        # 测试缺少参数的请求
        response = httpx.get('http://localhost:8888/api/user')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['error'], 'Missing id parameter')

    def test_custom_headers_and_delay(self):
        """测试自定义响应头和模拟网络延迟"""
        import time

        mock_server.set_mock_response('/api/slow-endpoint', {
            'status_code': 200,
            'headers': {
                'Content-type': 'application/json',
                'X-Custom-Header': 'custom-value',
                'X-Request-Id': 'req-12345',
                'Cache-Control': 'no-cache'
            },
            'body': {'message': 'Slow response'},
            'delay': 0.3  # 延迟 0.3 秒
        })

        start_time = time.time()
        response = httpx.get('http://localhost:8888/api/slow-endpoint')
        elapsed = time.time() - start_time

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['X-Custom-Header'], 'custom-value')
        self.assertEqual(response.headers['X-Request-Id'], 'req-12345')
        self.assertGreaterEqual(elapsed, 0.3)  # 验证延迟生效

    def test_different_http_methods_same_path(self):
        """测试同一路径对不同 HTTP 方法的响应"""

        def resource_handler(method, headers, body, query_params):
            """根据 HTTP 方法返回不同响应"""
            handlers = {
                'GET': lambda: {'action': 'get', 'data': 'resource data'},
                'POST': lambda: {'action': 'create', 'received': body},
                'PUT': lambda: {'action': 'update', 'updated': body},
                'DELETE': lambda: {'action': 'delete', 'success': True}
            }
            handler = handlers.get(method)
            return handler() if handler else {'error': 'Method not allowed'}

        mock_server.set_mock_callback('/api/resource', resource_handler)

        # 测试 GET
        resp = httpx.get('http://localhost:8888/api/resource')
        self.assertEqual(resp.json()['action'], 'get')

        # 测试 POST
        resp = httpx.post('http://localhost:8888/api/resource', json={'key': 'value'})
        self.assertEqual(resp.json()['action'], 'create')
        self.assertEqual(resp.json()['received']['key'], 'value')

        # 测试 PUT
        resp = httpx.put('http://localhost:8888/api/resource', json={'key': 'new_value'})
        self.assertEqual(resp.json()['action'], 'update')

        # 测试 DELETE
        resp = httpx.delete('http://localhost:8888/api/resource')
        self.assertEqual(resp.json()['action'], 'delete')

    def test_error_responses(self):
        """测试各种错误状态码"""
        # 404 Not Found
        mock_server.set_mock_response('/api/not-exists', {
            'status_code': 404,
            'body': {'error': 'Resource not found', 'code': 404}
        })

        response = httpx.get('http://localhost:8888/api/not-exists')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()['code'], 404)

        # 500 Internal Server Error
        mock_server.set_mock_response('/api/error', {
            'status_code': 500,
            'body': {'error': 'Internal server error', 'code': 500}
        })

        response = httpx.get('http://localhost:8888/api/error')
        self.assertEqual(response.status_code, 500)

    def test_isolation_first(self):
        """第一个测试：设置 Mock 数据"""
        mock_server.set_mock_response('/api/test-isolation', {
            'status_code': 200,
            'body': {'test': 'first'}
        })

        response = httpx.get('http://localhost:8888/api/test-isolation')
        self.assertEqual(response.json()['test'], 'first')
        # 测试结束后，Mock 数据会自动清理

    def test_isolation_second(self):
        """第二个测试：验证上一个测试的 Mock 已被清理"""
        # 上一个测试的 Mock 配置已被自动清理
        # 如果不重新设置，应该返回 404
        response = httpx.get('http://localhost:8888/api/test-isolation')
        self.assertEqual(response.status_code, 404)

        # 重新设置新的 Mock
        mock_server.set_mock_response('/api/test-isolation', {
            'status_code': 200,
            'body': {'test': 'second'}
        })

        response = httpx.get('http://localhost:8888/api/test-isolation')
        self.assertEqual(response.json()['test'], 'second')


if __name__ == '__main__':
    unittest.main()
