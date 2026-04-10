import pytest
import allure
from test_cases.base_test import PytestBaseTest
from common.utils import utils
from common.mock import mock_server

class TestHttpbin(PytestBaseTest):
    @allure.feature("Httpbin API")
    @allure.story("GET request")
    def test_get_request(self):
        response = self.send_request('get', '/get', params={'key': 'value'})
        assert response.status_code == 200
        assert response.json().get('args') == {'key': 'value'}
    
    @allure.feature("Httpbin API")
    @allure.story("POST request")
    def test_post_request(self):
        random_email = utils.generate_random_email()
        data = {
            "name": "Test User",
            "email": random_email,
            "age": utils.generate_random_number(18, 60)
        }
        response = self.send_request('post', '/post', json=data)
        assert response.status_code == 200
        assert response.json().get('json') == data
        
        # 提取响应中的数据
        self.extract_variable('email', random_email)
    
    @allure.feature("Httpbin API")
    @allure.story("PUT request")
    def test_put_request(self):
        email = self.get_variable('email')
        assert email is not None
        
        data = {
            "name": "Updated User",
            "email": email
        }
        response = self.send_request('put', '/put', json=data)
        assert response.status_code == 200
        assert response.json().get('json') == data
    
    @allure.feature("Httpbin API")
    @allure.story("DELETE request")
    def test_delete_request(self):
        response = self.send_request('delete', '/delete')
        assert response.status_code == 200
    
    @allure.feature("Httpbin API")
    @allure.story("Status code")
    def test_status_code(self):
        response = self.send_request('get', '/status/200')
        assert response.status_code == 200
    
    @allure.feature("Httpbin API")
    @allure.story("Headers")
    def test_headers(self):
        headers = {
            "X-Custom-Header": "custom-value"
        }
        response = self.send_request('get', '/headers', headers=headers)
        assert response.status_code == 200
        assert response.json().get('headers').get('X-Custom-Header') == 'custom-value'
    
    @allure.feature("Mock Server")
    @allure.story("Mock response")
    def test_mock_response(self):
        # 启动 mock 服务
        mock_server.start()
        
        # 设置 mock 响应
        mock_response = {
            "mock": True,
            "data": "This is a mock response"
        }
        mock_server.set_mock_response('/mock', mock_response)
        
        # 测试 mock 服务
        from common.request import Request
        mock_request = Request()
        mock_request.base_url = "http://localhost:8888"
        response = mock_request.get('/mock')
        assert response.status_code == 200
        assert response.json() == mock_response
        
        # 停止 mock 服务
        mock_server.stop()
