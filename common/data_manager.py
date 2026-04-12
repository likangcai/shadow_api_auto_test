# -*- coding: utf-8 -*-
# -----------------------------
# @Author    : 影子
# @Time      : 2025/3/10 10:55
# @Software  : PyCharm
# @FileName  : data_manager.py
# -----------------------------
import json
import yaml
import os
import pandas as pd
from pathlib import Path
from config.config import config

class DataManager:
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent
        self.data_dir = self.base_dir / "data"
    
    def read_data(self, file_name):
        file_path = self.data_dir / file_name
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File {file_name} not found in data directory")
        
        extension = file_path.suffix.lower()
        if extension == '.json':
            return self._read_json(file_path)
        elif extension == '.yaml' or extension == '.yml':
            return self._read_yaml(file_path)
        elif extension == '.xlsx' or extension == '.xls':
            return self._read_excel(file_path)
        else:
            raise ValueError(f"Unsupported file format: {extension}")
    
    def _read_json(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _read_yaml(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def _read_excel(self, file_path):
        df = pd.read_excel(file_path)
        return df.to_dict('records')

    def save_data(self, file_name, data):
        file_path = self.data_dir / file_name
        extension = file_path.suffix.lower()
        
        if extension == '.json':
            self._save_json(file_path, data)
        elif extension == '.yaml' or extension == '.yml':
            self._save_yaml(file_path, data)
        elif extension == '.xlsx':
            self._save_excel(file_path, data)
        else:
            raise ValueError(f"Unsupported file format: {extension}")
    
    def _save_json(self, file_path, data):
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def _save_yaml(self, file_path, data):
        with open(file_path, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, allow_unicode=True)
    
    def _save_excel(self, file_path, data):
        df = pd.DataFrame(data)
        df.to_excel(file_path, index=False)

data_manager = DataManager()
