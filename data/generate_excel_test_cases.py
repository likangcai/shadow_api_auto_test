# -*- coding: utf-8 -*-
# -----------------------------
# @Author    : 影子
# @Time      : 2025/3/11 12:08
# @Software  : PyCharm
# @FileName  : generate_excel_test_cases.py
# -----------------------------
import pandas as pd

# 创建测试用例数据
data = [
    {
        "name": "GET request test",
        "feature": "Httpbin API",
        "story": "GET request",
        "method": "get",
        "url": "/get",
        "params": '{"key": "value"}',
        "json": "{}",
        "headers": "{}",
        "assert": '{"status_code": 200, "json.args.key": "value"}'
    },
    {
        "name": "POST request test",
        "feature": "Httpbin API",
        "story": "POST request",
        "method": "post",
        "url": "/post",
        "params": "{}",
        "json": '{"name": "Test User", "email": "test@example.com"}',
        "headers": "{}",
        "assert": '{"status_code": 200, "json.json.name": "Test User"}'
    },
    {
        "name": "PUT request test",
        "feature": "Httpbin API",
        "story": "PUT request",
        "method": "put",
        "url": "/put",
        "params": "{}",
        "json": '{"name": "Updated User"}',
        "headers": "{}",
        "assert": '{"status_code": 200}'
    },
    {
        "name": "DELETE request test",
        "feature": "Httpbin API",
        "story": "DELETE request",
        "method": "delete",
        "url": "/delete",
        "params": "{}",
        "json": "{}",
        "headers": "{}",
        "assert": '{"status_code": 200}'
    }
]

# 创建 DataFrame
df = pd.DataFrame(data)

# 保存为 Excel 文件
df.to_excel('test_cases.xlsx', index=False)
print("Excel测试用例文件生成成功！")
