# -*- coding: utf-8 -*-
# -----------------------------
# @Author    : 影子
# @Time      : 2026/4/14 09:31
# @Software  : PyCharm
# @FileName  : test_mock_01.py
# -----------------------------
"""
Mock功能测试用例
包含HTTP Mock服务器和UnitTest Mock的使用示例
"""

import pytest
import httpx
from common.mock import mock_server, mock_helper, MockResponse


class TestHTTPMockServer:
    """HTTP Mock服务器测试"""

    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        """每个测试前后启动/停止Mock服务器"""
        mock_server.start()
        yield
        mock_server.stop()
        mock_server.clear_mock_responses()

    def test_simple_get_request(self):
        """测试简单的GET请求"""
        mock_server.set_mock_response('/api/users', {
            'status_code': 200,
            'body': {'users': [{'id': 1, 'name': 'Alice'}]}
        })

        response = httpx.get('http://localhost:8888/api/users')
        assert response.status_code == 200
        assert response.json() == {'users': [{'id': 1, 'name': 'Alice'}]}

    def test_post_with_static_response(self):
        """测试POST请求返回静态响应"""
        mock_server.set_mock_response('/api/users', {
            'status_code': 201,
            'body': {'id': 1, 'message': 'User created'}
        })

        response = httpx.post(
            'http://localhost:8888/api/users',
            json={'name': 'Bob', 'email': 'bob@example.com'}
        )
        assert response.status_code == 201
        assert response.json()['message'] == 'User created'

    def test_dynamic_callback_for_post(self):
        """测试使用回调函数动态处理POST请求"""
        def create_user_handler(method, headers, body, query_params):
            if method == 'POST':
                if body and body.get('name'):
                    return MockResponse(
                        status_code=201,
                        body={'id': 123, 'name': body['name'], 'created': True}
                    )
                return MockResponse(
                    status_code=400,
                    body={'error': 'Name is required'}
                )
            return {'status': 'ok'}

        mock_server.set_mock_callback('/api/users', create_user_handler)

        response = httpx.post(
            'http://localhost:8888/api/users',
            json={'name': 'Charlie'}
        )
        assert response.status_code == 201
        assert response.json()['name'] == 'Charlie'

        response = httpx.post(
            'http://localhost:8888/api/users',
            json={'email': 'no-name@example.com'}
        )
        assert response.status_code == 400

    def test_get_with_query_params(self):
        """测试GET请求带查询参数"""
        def query_handler(method, headers, body, query_params):
            user_id = query_params.get('id')
            if user_id:
                return {'user_id': user_id, 'name': f'User_{user_id}'}
            return {'error': 'Missing id parameter'}

        mock_server.set_mock_callback('/api/user', query_handler)

        response = httpx.get('http://localhost:8888/api/user?id=42')
        assert response.json() == {'user_id': '42', 'name': 'User_42'}

    def test_custom_headers_and_status(self):
        """测试自定义响应头和状态码"""
        mock_server.set_mock_response('/api/protected', {
            'status_code': 403,
            'headers': {
                'Content-type': 'application/json',
                'X-Custom-Header': 'custom-value'
            },
            'body': {'error': 'Forbidden'}
        })

        response = httpx.get('http://localhost:8888/api/protected')
        assert response.status_code == 403
        assert response.headers['X-Custom-Header'] == 'custom-value'

    def test_delayed_response(self):
        """测试延迟响应（模拟慢网络）"""
        mock_server.set_mock_response('/api/slow', {
            'status_code': 200,
            'body': {'message': 'Slow response'},
            'delay': 0.5
        })

        import time
        start = time.time()
        response = httpx.get('http://localhost:8888/api/slow')
        elapsed = time.time() - start

        assert response.status_code == 200
        assert elapsed >= 0.5

    def test_different_methods_same_path(self):
        """测试同一路径不同HTTP方法的响应"""
        def resource_handler(method, headers, body, query_params):
            if method == 'GET':
                return {'resource': 'data'}
            elif method == 'POST':
                return {'status': 'created', 'data': body}
            elif method == 'DELETE':
                return {'status': 'deleted'}
            return {'error': 'Method not allowed'}

        mock_server.set_mock_callback('/api/resource', resource_handler)

        get_resp = httpx.get('http://localhost:8888/api/resource')
        assert get_resp.json() == {'resource': 'data'}

        post_resp = httpx.post('http://localhost:8888/api/resource', json={'key': 'value'})
        assert post_resp.json()['status'] == 'created'

        delete_resp = httpx.delete('http://localhost:8888/api/resource')
        assert delete_resp.json() == {'status': 'deleted'}


class TestUnitTestMock:
    """UnitTest Mock测试"""

    def test_create_and_verify_mock(self):
        """测试创建和验证Mock对象"""
        api_mock = mock_helper.create_mock(name='api_client')
        api_mock.get_user.return_value = {'id': 1, 'name': 'test'}

        result = api_mock.get_user(123)
        assert result == {'id': 1, 'name': 'test'}

        assert mock_helper.verify_call(api_mock, call_count=1)

        history = mock_helper.get_call_history(api_mock)
        assert history['call_count'] == 1

        mock_helper.remove_mock('api_client')

    def test_patch_object_method(self):
        """测试Patch对象方法"""
        class SampleService:
            def fetch_data(self, query):
                return "real data"

        service = SampleService()
        fetch_mock = mock_helper.patch_object(service, 'fetch_data', return_value='mocked data')

        result = service.fetch_data("SELECT * FROM users")
        assert result == 'mocked data'

        fetch_mock.assert_called_once_with("SELECT * FROM users")

        mock_helper.unpatch_object(fetch_mock)
        assert service.fetch_data("query") == "real data"

    def test_mock_with_side_effect(self):
        """测试Mock的副作用功能"""
        api_mock = mock_helper.create_mock(name='api_with_side_effect')

        def side_effect(user_id):
            if user_id == 1:
                return {'id': 1, 'name': 'Alice'}
            elif user_id == 2:
                return {'id': 2, 'name': 'Bob'}
            raise ValueError(f"Unknown user: {user_id}")

        api_mock.get_user.side_effect = side_effect

        assert api_mock.get_user(1) == {'id': 1, 'name': 'Alice'}
        assert api_mock.get_user(2) == {'id': 2, 'name': 'Bob'}

        with pytest.raises(ValueError):
            api_mock.get_user(999)

        mock_helper.remove_mock('api_with_side_effect')

    def test_cleanup_after_test(self):
        """测试清理所有Mock"""
        mock_helper.create_mock(name='mock1')
        mock_helper.create_mock(name='mock2')

        mock_helper.clear_all_mocks()

        assert mock_helper.get_mock('mock1') is None
        assert mock_helper.get_mock('mock2') is None