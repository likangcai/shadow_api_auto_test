import os
import yaml
from pathlib import Path

class Config:
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent
        self.config_file = self.base_dir / "config" / "config.yaml"
        self.load_config()
    
    def load_config(self):
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r', encoding='utf-8') as f:
                self.config = yaml.safe_load(f)
        else:
            self.config = {
                "base_url": "http://localhost:8000",
                "timeout": 30,
                "verify_ssl": False,
                "test_runner": "pytest",  # pytest or unittest
                "data_format": "yaml",  # yaml, json, excel
                "reports": {
                    "allure": True,
                    "html": True
                },
                "push": {
                    "email": False,
                    "dingtalk": False,
                    "feishu": False,
                    "wecom": False
                }
            }
    
    def get(self, key, default=None):
        keys = key.split('.')
        value = self.config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value
    
    def set(self, key, value):
        keys = key.split('.')
        config = self.config
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        config[keys[-1]] = value

config = Config()
