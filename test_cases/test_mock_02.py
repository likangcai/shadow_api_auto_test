# -*- coding: utf-8 -*-
# -----------------------------
# @Author    : 影子
# @Time      : 2026/4/14 10:19
# @Software  : PyCharm
# @FileName  : test_mock_02.py
# -----------------------------
import pytest
import httpx
from common.mock import mock_server, MockResponse


class TestMockServerUsage:
    """Mock 服务器使用示例"""

    @pytest.fixture(autouse=True)
    def setup_and_teardown(self):
        """每个测试用例前后自动启动/停止 Mock 服务器"""
        mock_server.start()
        yield
        mock_server.stop()
        mock_server.clear_mock_responses()

    def test_simple_get(self):
        """测试简单 GET 请求"""
        # 设置静态响应
        mock_server.set_mock_response('/api/test', {
            'status_code': 200,
            'body': {'message': 'Hello World'}
        })

        # 发起请求
        response = httpx.get('http://localhost:8888/api/test')

        # 验证响应
        assert response.status_code == 200
        assert response.json() == {'message': 'Hello World'}

    def test_post_with_callback(self):
        """测试 POST 请求使用动态回调"""

        def handle_create(method, headers, body, query_params):
            """动态处理创建用户请求"""
            if body and body.get('name'):
                return {
                    'status_code': 201,
                    'body': {
                        'id': 123,
                        'name': body['name'],
                        'message': 'User created successfully'
                    }
                }
            return {
                'status_code': 400,
                'body': {'error': 'Name is required'}
            }

        mock_server.set_mock_callback('/api/users', handle_create)

        # 测试成功场景
        response = httpx.post(
            'http://localhost:8888/api/users',
            json={'name': 'Bob', 'email': 'bob@example.com'}
        )
        assert response.status_code == 201
        assert response.json()['name'] == 'Bob'

        # 测试失败场景
        response = httpx.post(
            'http://localhost:8888/api/users',
            json={'email': 'noname@example.com'}
        )
        assert response.status_code == 400

    def test_query_params(self):
        """测试带查询参数的 GET 请求"""

        def handle_user_query(method, headers, body, query_params):
            user_id = query_params.get('id')
            if user_id:
                return {
                    'user_id': user_id,
                    'name': f'User_{user_id}'
                }
            return {'error': 'Missing id parameter'}

        mock_server.set_mock_callback('/api/user', handle_user_query)

        response = httpx.get('http://localhost:8888/api/user?id=42')
        assert response.json() == {'user_id': '42', 'name': 'User_42'}

    def test_custom_headers_and_delay(self):
        """测试自定义响应头和延迟"""
        mock_server.set_mock_response('/api/slow', {
            'status_code': 200,
            'headers': {
                'Content-type': 'application/json',
                'X-Custom-Header': 'test-value',
                'X-Request-Id': 'abc-123'
            },
            'body': {'data': 'slow response'},
            'delay': 0.5  # 延迟 0.5 秒
        })

        import time
        start = time.time()
        response = httpx.get('http://localhost:8888/api/slow')
        elapsed = time.time() - start

        assert response.status_code == 200
        assert response.headers['X-Custom-Header'] == 'test-value'
        assert elapsed >= 0.5  # 验证延迟生效

    def test_different_http_methods(self):
        """测试同一路径不同 HTTP 方法"""

        def resource_handler(method, headers, body, query_params):
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
        assert resp.json()['action'] == 'get'

        # 测试 POST
        resp = httpx.post('http://localhost:8888/api/resource', json={'key': 'value'})
        assert resp.json()['action'] == 'create'

        # 测试 DELETE
        resp = httpx.delete('http://localhost:8888/api/resource')
        assert resp.json()['action'] == 'delete'
