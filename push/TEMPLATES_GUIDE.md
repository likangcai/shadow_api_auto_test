# 消息推送模板使用说明

## 概述

消息推送系统已升级为支持 **Markdown 模板**，各个平台（钉钉、飞书、企业微信）都有独立的模板文件，支持变量自动替换。

## 目录结构

```
push/
├── templates/              # 消息模板目录
│   ├── dingtalk.md        # 钉钉消息模板
│   ├── feishu.md          # 飞书消息模板
│   └── wecom.md           # 企业微信消息模板
├── template_manager.py    # 模板管理器
├── dingtalk.py            # 钉钉推送
├── feishu.py              # 飞书推送
├── wecom.py               # 企业微信推送
└── push_manager.py        # 推送管理器
```

## 支持的变量

所有模板支持以下变量：

### 项目信息变量（从 config.yaml 自动读取）

| 变量名 | 说明 | 来源 | 示例 |
|--------|------|------|------|
| `{project_name}` | 项目名称 | `config.yaml` -> `project.name` | API自动化测试项目 |
| `{environment}` | 运行环境 | `config.yaml` -> `project.environment` | 测试环境 |
| `{executor}` | 执行人 | `config.yaml` -> `project.executor`（为空则显示“🤖 自动触发”） | 🤖 自动触发 |
| `{start_time}` | 开始执行时间 | 测试开始时自动记录 | 2026-04-14 13:00:00 |

### 测试结果变量

| 变量名 | 说明 | Allure 对应 | 示例 |
|--------|------|------------|------|
| `{title}` | 报告标题 | - | API自动化测试报告 |
| `{total}` | 用例总数 | total | 35 |
| `{passed}` | 通过数 | passed | 24 |
| `{failed}` | 失败数 | failed | 6 |
| `{errors}` | 错误数 | - | 0 |
| `{broken}` | 中断数 | broken | 3 |
| `{skipped}` | 跳过数 | skipped | 2 |
| `{unknown}` | 未知数 | unknown | 0 |
| `{duration}` | 执行耗时 | - | 180s |
| `{pass_rate}` | 通过率（基于执行的用例，不包括跳过和未知） | - | 72.73 |
| `{report_url}` | 报告链接 | - | http://example.com/report.html |
| `{time}` | 结束时间 | - | 2026-04-14 13:05:00 |

**注意**：
- `errors` 和 `broken` 的区别：
  - `errors`: unittest 风格的错误（如断言失败、异常等）
  - `broken`: Allure 风格的中断（如环境问题、依赖不可用等）
- `unknown`: Allure 风格的未知状态（极少出现）
- 邮件 HTML 会智能隐藏值为 0 的字段

## 使用方式

### 方式一：自动发送（推荐）

测试完成后会自动使用模板发送消息：

```python
from runner.runner import runner

# 运行测试，自动发送通知
result = runner.run_with_pytest()
# 或
result = runner.run_with_unittest()
```

### 方式二：手动发送

```python
from push.push_manager import push_manager

# 准备测试数据
test_result = {
    'total': 100,
    'passed': 95,
    'failed': 3,
    'errors': 2,
    'duration': '120s'
}

# 发送通知（自动使用模板）
push_manager.send_notification(
    subject='API自动化测试报告',
    test_result=test_result
)
```

### 方式三：自定义变量

```python
from push.dingtalk import dingtalk_push

# 自定义变量
variables = {
    'title': '自定义标题',
    'total': 50,
    'passed': 48,
    'failed': 2,
    'errors': 0,
    'duration': '60s',
    'pass_rate': 96.0,
    'report_url': 'http://example.com',
    'time': '2026-04-14 13:00:00'
}

# 发送钉钉消息
dingtalk_push.send(variables=variables)
```

## 自定义模板

### 1. 编辑模板文件

直接修改 `push/templates/` 下的 Markdown 文件：

```markdown
## 📊 {title}

### 项目信息

- 项目名称: {project_name}
- 运行环境: {environment}
- 执行人: {executor}
- 开始时间: {start_time}

### 测试结果

- 总数: {total}
- 通过: {passed}
- 失败: {failed}
```

### 2. 配置项目信息

在 `config.yaml` 中配置项目信息：

```yaml
project:
  name: "API自动化测试项目"  # 项目名称
  environment: "测试环境"      # 运行环境
  executor: "张三"             # 执行人（留空则为自动触发）
```

**注意**：
- 如果 `executor` 为空字符串，消息中会显示 "🤖 自动触发"
- `start_time` 会在测试开始时自动记录，无需手动配置

### 3. 添加新变量

在模板中使用 `{变量名}` 格式：

```markdown
### 新增指标

- 自定义指标: {custom_metric}
```

然后在发送时传入该变量：

```python
variables = {
    'title': '测试报告',
    'custom_metric': '自定义值',
    # ... 其他变量
}
push_manager.send_notification(test_result=variables)
```

## 各平台特性

### 钉钉 (DingTalk)

- **消息类型**: Markdown
- **支持特性**: 
  - ✅ 表格
  - ✅ 链接
  - ✅ 粗体/斜体
  - ✅ Emoji 表情
  - ✅ 引用块

### 飞书 (FeiShu)

- **消息类型**: Post（富文本）
- **支持特性**:
  - ✅ 纯文本内容
  - ⚠️ 不支持 Markdown 语法（会显示为纯文本）
  - ✅ 支持换行

### 企业微信 (WeCom)

- **消息类型**: Markdown
- **支持特性**:
  - ✅ 标题 (# ## ###)
  - ✅ 粗体 (**text**)
  - ✅ 链接 [text](url)
  - ✅ 列表 (- item)
  - ✅ 引用 (> text)
  - ⚠️ 不支持表格

## 注意事项

1. **飞书限制**: 飞书的 post 消息类型不支持完整的 Markdown，建议简化模板
2. **企业微信限制**: 不支持表格，如需表格请用文本形式展示
3. **变量缺失**: 如果模板中的变量未提供，会保留原始占位符 `{变量名}`
4. **向后兼容**: 仍然支持旧的 `send(content)` 方式
5. **跳过用例**: 
   - 跳过的用例会从通过率计算中排除
   - 通过率 = (通过数 / 执行数) × 100%，其中执行数 = 总数 - 跳过数 - 未知数
   - 例如：35个用例，2个跳过，0个未知，24个通过，则通过率 = 24/(35-2-0) × 100% = 72.73%
6. **Allure 兼容性**:
   - 支持 Allure 的 `broken`（中断）和 `unknown`（未知）状态
   - 邮件 HTML 会智能隐藏值为 0 的字段，保持消息简洁

## 示例输出

### 钉钉/企业微信效果

```
## 📊 API自动化测试报告

---

### 📋 项目信息

| 项目 | 值 |
|------|------|
| 项目名称 | API自动化测试项目 |
| 运行环境 | 测试环境 |
| 执行人 | 🤖 自动触发 |
| 开始时间 | 2026-04-14 12:00:00 |

---

### ✅ 测试结果概览

| 指标 | 数量 |
|------|------|
| 📊 用例总数 | 100 |
| ✅ 通过 | 85 |
| ❌ 失败 | 5 |
| ⚠️ 错误 | 2 |
| ⏭️ 跳过 | 8 |
| ⏱️ 耗时 | 120s |

---

### 📈 成功率

**通过率**: 92.39%

---

### 🔗 相关链接

- 📄 查看详细报告
- 🕐 执行时间: 2026-04-14 13:00:00
```

## 故障排查

### 问题1: 消息发送失败

**检查**:
1. Webhook 地址是否正确配置
2. 网络连接是否正常
3. 查看日志中的错误信息

### 问题2: 变量未替换

**检查**:
1. 变量名是否与模板中一致
2. 是否传入了 `variables` 参数
3. 查看 `template_manager.py` 的日志

### 问题3: 模板未加载

**检查**:
1. `push/templates/` 目录是否存在
2. 模板文件是否是 `.md` 格式
3. 文件编码是否为 UTF-8

## 扩展开发

### 添加新的推送平台

1. 在 `push/templates/` 创建模板文件（如 `slack.md`）
2. 创建推送类（如 `push/slack.py`）
3. 在 `push_manager.py` 中集成

### 自定义模板逻辑

修改 `template_manager.py` 中的 `render()` 方法，添加更复杂的变量处理逻辑。
