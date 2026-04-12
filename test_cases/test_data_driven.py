# -*- coding: utf-8 -*-
# -----------------------------
# @Author    : 影子
# @Time      : 2025/3/12 16:30
# @Software  : PyCharm
# @FileName  : test_data_driven.py
# -----------------------------
import pytest
import allure
from test_cases.base_test import PytestBaseTest
from common.test_case_loader import test_case_loader

class TestDataDriven(PytestBaseTest):
    @pytest.mark.parametrize("test_case", test_case_loader.load_test_cases("test_cases.yaml"))
    @allure.feature("Data Driven Tests")
    def test_from_yaml(self, test_case):
        method = test_case.get('method', 'get')
        url = test_case.get('url', '')
        params = test_case.get('params', {})
        json_data = test_case.get('json', {})
        headers = test_case.get('headers', {})
        
        response = self.send_request(method, url, params=params, json=json_data, headers=headers)
        
        # 执行断言
        assertions = test_case.get('assert', {})
        for key, expected_value in assertions.items():
            if key == 'status_code':
                assert response.status_code == expected_value
            elif key.startswith('json.'):
                # 解析 json 路径，如 json.args.key
                json_path = key.split('.')[1:]
                actual_value = response.json()
                for path in json_path:
                    if isinstance(actual_value, dict) and path in actual_value:
                        actual_value = actual_value[path]
                    else:
                        actual_value = None
                        break
                assert actual_value == expected_value
    
    @pytest.mark.parametrize("test_case", test_case_loader.load_test_cases("test_cases.json"))
    @allure.feature("Data Driven Tests")
    def test_from_json(self, test_case):
        method = test_case.get('method', 'get')
        url = test_case.get('url', '')
        params = test_case.get('params', {})
        json_data = test_case.get('json', {})
        headers = test_case.get('headers', {})
        
        response = self.send_request(method, url, params=params, json=json_data, headers=headers)
        
        # 执行断言
        assertions = test_case.get('assert', {})
        for key, expected_value in assertions.items():
            if key == 'status_code':
                assert response.status_code == expected_value
            elif key.startswith('json.'):
                # 解析 json 路径，如 json.args.key
                json_path = key.split('.')[1:]
                actual_value = response.json()
                for path in json_path:
                    if isinstance(actual_value, dict) and path in actual_value:
                        actual_value = actual_value[path]
                    else:
                        actual_value = None
                        break
                assert actual_value == expected_value
