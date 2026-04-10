import json
import yaml
import pandas as pd
import os
from pathlib import Path
from common.log import log

class TestCaseLoader:
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent
        self.data_dir = self.base_dir / "data"
    
    def load_test_cases(self, file_name):
        file_path = self.data_dir / file_name
        if not os.path.exists(file_path):
            log.error(f"Test case file {file_name} not found")
            return []
        
        extension = file_path.suffix.lower()
        if extension == '.json':
            return self._load_json(file_path)
        elif extension == '.yaml' or extension == '.yml':
            return self._load_yaml(file_path)
        elif extension == '.xlsx' or extension == '.xls':
            return self._load_excel(file_path)
        else:
            log.error(f"Unsupported file format: {extension}")
            return []
    
    def _load_json(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data.get('test_cases', [])
        except Exception as e:
            log.error(f"Failed to load JSON test cases: {str(e)}")
            return []
    
    def _load_yaml(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            return data.get('test_cases', [])
        except Exception as e:
            log.error(f"Failed to load YAML test cases: {str(e)}")
            return []
    
    def _load_excel(self, file_path):
        try:
            df = pd.read_excel(file_path)
            test_cases = []
            for _, row in df.iterrows():
                test_case = {
                    "name": row.get('name', ''),
                    "feature": row.get('feature', ''),
                    "story": row.get('story', ''),
                    "method": row.get('method', 'get'),
                    "url": row.get('url', ''),
                    "params": self._parse_json(row.get('params', '{}')),
                    "json": self._parse_json(row.get('json', '{}')),
                    "headers": self._parse_json(row.get('headers', '{}')),
                    "assert": self._parse_json(row.get('assert', '{}'))
                }
                test_cases.append(test_case)
            return test_cases
        except Exception as e:
            log.error(f"Failed to load Excel test cases: {str(e)}")
            return []
    
    def _parse_json(self, json_str):
        if not json_str:
            return {}
        try:
            return json.loads(json_str)
        except Exception:
            return {}

test_case_loader = TestCaseLoader()
