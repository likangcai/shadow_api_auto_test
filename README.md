# API 自动化测试框架

基于 Python 技术栈的通用接口自动化测试框架，支持多种测试用例格式、消息推送、测试报告生成等功能。

## 功能特性

- ✅ 封装公共通用方法
- ✅ 支持接口用例之间的关联复用
- ✅ 测试用例支持 JSON/Excel/YAML/Py 格式
- ✅ **智能消息推送**（邮件/钉钉/飞书/企微，Markdown 模板，变量自动替换）
- ✅ 参数化可配置
- ✅ **支持 unittest、pytest 和混合模式三种执行方式**
- ✅ **强大的 Mock 服务**（HTTP 级别 + 对象级别）
- ✅ **Mock 端口配置化**（支持自定义端口）
- ✅ **内置 Allure 工具**（无需系统安装）
- ✅ 支持假数据生成
- ✅ 支持错误重试机制
- ✅ 支持多线程执行
- ✅ **灵活的 Mock 启用/禁用控制**

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
│   ├── mock.py        # Mock 服务（HTTP + 对象级别）
│   ├── mock_helper.py # Mock 辅助工具（新增）
│   └── utils.py       # 工具类（假数据生成等）
├── config/            # 配置文件
│   ├── __init__.py
│   ├── config.py      # 配置类
│   └── config.yaml    # 配置文件（含 Mock 端口配置）
├── data/              # 测试数据
│   └── __init__.py
├── push/              # 消息推送
│   ├── __init__.py
│   ├── templates/     # Markdown 消息模板（新增）
│   │   ├── dingtalk.md
│   │   ├── feishu.md
│   │   └── wecom.md
│   ├── template_manager.py # 模板管理器（新增）
│   ├── email.py       # 邮件推送
│   ├── dingtalk.py    # 钉钉推送
│   ├── feishu.py      # 飞书推送
│   ├── wecom.py       # 企微推送
│   └── push_manager.py # 推送管理
├── reports/           # 测试报告
│   └── __init__.py
├── runner/            # 测试运行器
│   ├── __init__.py
│   ├── runner.py      # 运行器
│   └── allure/        # 内置 Allure 工具
│       ├── bin/
│       ├── config/
│       ├── lib/
│       └── plugins/
├── test_cases/        # 测试用例
│   ├── __init__.py
│   ├── base_test.py   # 测试基类（支持 Mock 启用/禁用）
│   ├── test_pytest_mock_example.py    # Pytest Mock 示例
│   ├── test_unittest_mock_example.py  # Unittest Mock 示例
│   ├── test_disable_mock_example.py   # 禁用 Mock 示例
│   └── test_without_mock.py           # 不使用 Mock 示例
├── main.py            # 主入口
└── requirements.txt   # 依赖文件
```

## 安装依赖

```bash
pip install -r requirements.txt
```

## 配置说明

修改 `config/config.yaml` 文件，配置以下内容：

### 基础配置
- `base_url`: API 基础 URL
- `timeout`: 请求超时时间
- `verify_ssl`: 是否验证 SSL
- `test_runner`: 测试运行器（**pytest** / **unittest** / **mixed**）
  - `pytest`: 只运行 pytest 测试
  - `unittest`: 只运行 unittest 测试
  - `mixed`: 混合模式，先运行 unittest 再运行 pytest，合并结果
- `retry_count`: 错误重试次数
- `retry_interval`: 重试间隔（秒）
- `thread_count`: 线程数

### 项目信息配置
```yaml
project:
  name: "API自动化测试项目"   # 项目名称
  environment: "test"         # 运行环境：test(测试)/uat(预发布)/prod(生产)
  executor: ""                # 执行人（留空则显示"🤖 自动触发"）
  title: "API自动化测试报告"   # 测试报告标题（用于HTML报告和消息推送）
```

**注意**：`title` 字段统一控制 HTML 报告标题和消息推送中的报告标题。

### Mock 服务配置（新增）
```yaml
mock_server:
  host: "localhost"
  port: 8899  # Mock 服务器端口，可自定义
```

### 测试报告配置
```yaml
reports:
  allure: false                   # 是否生成 Allure 报告
  html: true                      # 是否生成 HTML 报告
  report_url: "https://example.com/reports/html/report.html"  # 报告访问地址（可选）
  pytest_xhtml:
    css: []                       # 自定义 CSS 文件列表
  xtestrunner:
    description: "API自动化测试报告"  # 报告描述
    language: "zh-CN"             # 语言：zh-CN(中文) / en(英文)
    retry: 0                      # 重试次数
```

**report_url 说明**：
- 用于消息推送中的报告链接
- 如果不配置，将自动使用 `base_url + /reports/html/report.html`
- 建议配置为实际的报告服务器地址，如 CI/CD 平台的报告 URL

**title 配置说明**：
- 报告标题已从 `reports.xtestrunner.title` 移动到 `project.title`
- 统一控制 XTestRunner HTML 报告标题和所有消息推送中的报告标题
- 修改一处即可同时影响所有地方

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

### Mock 服务（增强版）

#### 1. HTTP Mock 服务器

**方式一：使用辅助函数（推荐）**
```python
from common.mock_helper import mock_get, mock_post, mock_put, mock_delete
from common.mock import mock_server

# 设置 Mock 响应
mock_server.set_mock_response('/api/users', {
    'status_code': 200,
    'body': {'users': [{'id': 1, 'name': 'Alice'}]}
})

# 发送请求（自动使用配置的端口）
response = mock_get('/api/users')
assert response.status_code == 200
```

**方式二：动态回调**
```python
from common.mock import mock_server, MockResponse

def user_handler(method, headers, body, query_params):
    if method == 'POST' and body.get('name'):
        return MockResponse(
            status_code=201,
            body={'id': 123, 'name': body['name'], 'created': True}
        )
    return {'error': 'Invalid request'}

mock_server.set_mock_callback('/api/users', user_handler)
```

**方式三：获取 Mock URL**
```python
from common.mock_helper import get_mock_url
import httpx

url = get_mock_url('/api/users')  # http://localhost:8899/api/users
response = httpx.get(url)
```

#### 2. 对象级别 Mock（UnitTestMock）

```python
from common.mock import mock_helper

# 创建 Mock 对象
api_mock = mock_helper.create_mock(name='api_client')
api_mock.get_user.return_value = {'id': 1, 'name': 'test'}

# 使用 Mock
result = api_mock.get_user(123)
assert result == {'id': 1, 'name': 'test'}

# 验证调用
assert mock_helper.verify_call(api_mock, call_count=1)
```

#### 3. 禁用 Mock 服务

如果某些测试类不需要 Mock，可以禁用：

```python
from test_cases.base_test import PytestBaseTest

class TestRealAPI(PytestBaseTest):
    _enable_mock = False  # 禁用 Mock
    
    def test_real_api(self):
        # 这个测试会调用真实 API
        response = self.send_request('get', 'https://httpbin.org/get')
        assert response.status_code == 200
```

#### 4. Mock 配置说明

- **端口配置**：在 `config.yaml` 中修改 `mock_server.port`
- **自动管理**：继承基类后，Mock 服务器自动启动/停止
- **用例隔离**：每个测试用例后自动清理 Mock 数据
- **灵活控制**：通过 `_enable_mock` 标志位选择性启用

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

### Allure 报告（无需安装）

项目已内置 Allure 工具（`runner/allure/`），**无需系统安装**即可生成报告：

```bash
python main.py
```

Allure 会自动从项目目录执行，生成的报告位于：
- `reports/allure-results/`: Allure 原始数据
- `reports/allure-report/`: Allure HTML 报告

**自动打开报告**：测试完成后，Allure 报告会**自动在浏览器中打开**，无需手动操作。

如需手动打开报告：
```bash
# 使用内置 Allure 打开报告
runner/allure/bin/allure.bat open reports/allure-report  # Windows
runner/allure/bin/allure open reports/allure-report      # Linux/Mac

# 或者直接使用 allure open 命令
allure open reports/allure-report
```

### HTML 报告

- `reports/html/report.html`: XTestRunner 生成的 HTML 报告

### 报告配置

在 `config.yaml` 中配置：
```yaml
reports:
  allure: true   # 启用 Allure 报告
  html: true     # 启用 HTML 报告
```

## 消息推送

测试完成后会自动发送格式化的测试报告，支持以下推送方式：

- **邮件推送** - HTML 格式，包含项目信息和测试结果表格
- **钉钉推送** - Markdown 格式，支持富文本展示
- **飞书推送** - Post 富文本格式
- **企微推送** - Markdown 格式

### 消息特性

✅ **Markdown 模板**：各平台有独立的 Markdown 模板文件（`push/templates/`）  
✅ **变量自动替换**：从 `config.yaml` 自动读取项目信息，测试开始时自动记录时间  
✅ **智能显示**：邮件 HTML 会隐藏值为 0 的字段，保持消息简洁  
✅ **Allure 兼容**：完整支持 Allure 的所有状态（passed/failed/broken/skipped/unknown）  
✅ **通过率计算**：基于执行的用例数（排除跳过和未知），更准确反映测试质量

### 配置示例

```yaml
# config.yaml

# 项目信息（会在消息中显示）
project:
  name: "API自动化测试项目"
  environment: "测试环境"
  executor: ""  # 留空则显示“🤖 自动触发”

# 启用推送
push:
  email: false
  dingtalk: true
  feishu: false
  wecom: true

# 钉钉配置
dingtalk:
  webhook: "https://oapi.dingtalk.com/robot/send?access_token=xxx"
  secret: "your_secret"

# 企业微信配置
wecom:
  webhook: "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=xxx"
```

### 消息内容示例

**钉钉/企微收到的消息**：

```
## 📊 API自动化测试报告

### 📋 项目信息

| 项目 | 值 |
|------|------|
| 项目名称 | API自动化测试项目 |
| 运行环境 | 测试环境 |
| 执行人 | 🤖 自动触发 |
| 开始时间 | 2026-04-14 12:00:00 |

### ✅ 测试结果概览

| 指标 | 数量 |
|------|------|
| 📊 用例总数 | 35 |
| ✅ 通过 | 24 |
| ❌ 失败 | 6 |
| 💥 中断 | 3 |
| ⏭️ 跳过 | 2 |
| ⏱️ 耗时 | 180s |

### 📈 成功率

**通过率**: 72.73%
```

详细使用说明请参考：[push/TEMPLATES_GUIDE.md](push/TEMPLATES_GUIDE.md)

## 配置示例

项目提供了完整的配置示例文件 `config/config.example.yaml`，包含：
- ✅ 所有配置项的详细说明
- ✅ 合理的默认值
- ✅ 安全建议（敏感信息使用占位符）
- ✅ 最佳实践指南

**快速开始**：
```bash
# 复制示例文件
cp config/config.example.yaml config/config.yaml

# 编辑配置文件，根据实际情况修改
# 然后运行测试
python main.py
```

详细配置说明请参考：[config/config.example.yaml](config/config.example.yaml)

## 注意事项

1. **Allure 工具**：项目已内置 Allure，无需系统安装。如需使用系统版本，确保其在 PATH 中
2. **Mock 端口**：默认端口为 8899，可在 `config.yaml` 中修改。如端口冲突，请更换端口
3. **消息推送**：需要在配置文件中启用并配置相应的服务参数。支持自定义 Markdown 模板（见 `push/templates/`）
4. **多线程执行**：可能会影响测试稳定性，建议根据实际情况调整线程数
5. **Mock 启用控制**：通过 `_enable_mock = False` 可以禁用特定测试类的 Mock 服务
6. **URL 管理**：推荐使用 `mock_helper` 辅助函数，避免硬编码 URL
7. **执行人配置**：在 `config.yaml` 中配置 `project.executor`，留空则显示"🤖 自动触发"
8. **报告标题**：统一使用 `project.title` 配置，同时影响 HTML 报告和消息推送
9. **邮件端口**：QQ 邮箱使用端口 587（STARTTLS），如需使用 SSL 请改为端口 465
10. **配置示例**：首次使用建议参考 `config/config.example.yaml` 文件

## 联系方式

如有问题或建议，欢迎通过 Issue 反馈。

作者：影子<br>
邮箱：yingzilkq@163.com<br>
Gitee仓库地址：https://gitee.com/yingzi_shadow/shadow_api_auto_test<br>
微信公众号：前行的影子