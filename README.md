# API 自动化测试框架

基于 Python 技术栈的通用接口自动化测试框架，支持多种测试用例格式、消息推送、测试报告生成等功能。

## 功能特性

- ✅ 封装公共通用方法
- ✅ 支持接口用例之间的关联复用
- ✅ 测试用例支持 JSON/Excel/YAML/Py 格式
- ✅ 支持测试完成后的消息推送（邮件、钉钉、飞书、企微）
- ✅ 参数化可配置
- ✅ 支持 unittest 和 pytest 执行方式
- ✅ 支持 Mock 服务
- ✅ 支持假数据生成
- ✅ 支持错误重试机制
- ✅ 支持多线程执行

## 项目结构

```
api_auto_test/
├── __init__.py
├── common/            # 公共通用方法
│   ├── __init__.py
│   ├── request.py     # 请求封装
│   ├── log.py         # 日志管理
│   ├── data_manager.py # 数据管理
│   ├── case_relation.py # 用例关联管理
│   ├── mock.py        # Mock 服务
│   └── utils.py       # 工具类（假数据生成等）
├── config/            # 配置文件
│   ├── __init__.py
│   ├── config.py      # 配置类
│   └── config.yaml    # 配置文件
├── data/              # 测试数据
│   └── __init__.py
├── push/              # 消息推送
│   ├── __init__.py
│   ├── email.py       # 邮件推送
│   ├── dingtalk.py    # 钉钉推送
│   ├── feishu.py      # 飞书推送
│   ├── wecom.py       # 企微推送
│   └── push_manager.py # 推送管理
├── reports/           # 测试报告
│   └── __init__.py
├── runner/            # 测试运行器
│   ├── __init__.py
│   └── runner.py      # 运行器
├── test_cases/        # 测试用例
│   ├── __init__.py
│   ├── base_test.py   # 测试基类
│   ├── test_example.py # 示例测试用例
│   └── test_httpbin.py # httpbin 测试用例
├── main.py            # 主入口
└── requirements.txt   # 依赖文件
```

## 安装依赖

```bash
pip install -r requirements.txt
```

## 配置说明

修改 `config/config.yaml` 文件，配置以下内容：

- `base_url`: API 基础 URL
- `timeout`: 请求超时时间
- `verify_ssl`: 是否验证 SSL
- `test_runner`: 测试运行器（pytest 或 unittest）
- `data_format`: 测试数据格式（yaml、json、excel）
- `reports`: 测试报告配置
- `push`: 消息推送配置
- `email`: 邮件推送配置
- `dingtalk`: 钉钉推送配置
- `feishu`: 飞书推送配置
- `wecom`: 企微推送配置

## 运行测试

```bash
python main.py
```

## 测试用例编写

### Python 格式测试用例

```python
import pytest
import allure
from test_cases.base_test import PytestBaseTest
from common.utils import utils

class TestExample(PytestBaseTest):
    @allure.feature("Example API")
    @allure.story("GET request")
    def test_get_request(self):
        response = self.send_request('get', '/get', params={'key': 'value'})
        assert response.status_code == 200
        assert response.json().get('args') == {'key': 'value'}
```

### YAML 格式测试用例

创建 `data/test_cases.yaml` 文件：

```yaml
test_cases:
  - name: "GET request"
    feature: "Example API"
    story: "GET request"
    method: "get"
    url: "/get"
    params: {"key": "value"}
    assert:
      status_code: 200
      json.args.key: "value"
```

### JSON 格式测试用例

创建 `data/test_cases.json` 文件：

```json
{
  "test_cases": [
    {
      "name": "GET request",
      "feature": "Example API",
      "story": "GET request",
      "method": "get",
      "url": "/get",
      "params": {"key": "value"},
      "assert": {
        "status_code": 200,
        "json.args.key": "value"
      }
    }
  ]
}
```

### Excel 格式测试用例

创建 `data/test_cases.xlsx` 文件，包含以下列：
- name: 测试用例名称
- feature: 功能模块
- story: 测试场景
- method: 请求方法
- url: 请求路径
- params: 请求参数（JSON 格式）
- json: 请求体（JSON 格式）
- headers: 请求头（JSON 格式）
- assert: 断言（JSON 格式）

## 高级功能

### 错误重试机制

在 `common/request.py` 中已实现错误重试机制，可在配置文件中设置重试次数和间隔时间。

### 多线程执行

在 `runner/runner.py` 中已实现多线程执行测试用例的功能，可在配置文件中设置线程数。

### Mock 服务

```python
from common.mock import mock_server

# 启动 mock 服务
mock_server.start()

# 设置 mock 响应
mock_server.set_mock_response('/mock', {"mock": True, "data": "This is a mock response"})

# 测试完成后停止 mock 服务
mock_server.stop()
```

### 假数据生成

```python
from common.utils import utils

# 生成随机字符串
random_str = utils.generate_random_string(10)

# 生成随机邮箱
random_email = utils.generate_random_email()

# 生成随机手机号
random_phone = utils.generate_random_phone()

# 生成随机数字
random_number = utils.generate_random_number(1, 100)

# 生成随机日期
random_date = utils.generate_random_date()

# 生成随机布尔值
random_bool = utils.generate_random_boolean()
```

### 用例关联

```python
# 在第一个测试用例中提取变量
user_id = response.json().get('id')
self.extract_variable('user_id', user_id)

# 在第二个测试用例中使用变量
user_id = self.get_variable('user_id')
assert user_id is not None
```

## 测试报告

测试完成后，会在 `reports` 目录下生成测试报告：

- `html/report.html`: HTML 格式测试报告
- `allure-results/`: Allure 测试报告原始数据
- `allure-report/`: Allure 测试报告（需要安装 allure 命令行工具）

## 消息推送

在配置文件中启用相应的推送方式，测试完成后会自动发送测试报告：

- 邮件推送
- 钉钉推送
- 飞书推送
- 企微推送

## 注意事项

1. 执行 Allure 测试报告需要安装 allure 命令行工具
2. 消息推送需要配置相应的服务参数
3. 多线程执行可能会影响测试的稳定性，建议根据实际情况调整线程数
