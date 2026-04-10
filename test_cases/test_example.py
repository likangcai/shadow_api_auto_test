import pytest
import allure
from test_cases.base_test import PytestBaseTest

class TestExample(PytestBaseTest):
    @allure.feature("Example API")
    @allure.story("Get user info")
    def test_get_user_info(self):
        response = self.send_request('get', '/api/users/1')
        assert response.status_code == 200
        
        user_id = response.json().get('id')
        self.extract_variable('user_id', user_id)
    
    @allure.feature("Example API")
    @allure.story("Update user info")
    def test_update_user_info(self):
        user_id = self.get_variable('user_id')
        assert user_id is not None
        
        data = {
            "name": "Updated User",
            "email": "updated@example.com"
        }
        
        response = self.send_request('put', f'/api/users/{user_id}', json=data)
        assert response.status_code == 200
