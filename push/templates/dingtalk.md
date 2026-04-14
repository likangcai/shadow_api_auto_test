# 钉钉消息模板
# 支持变量: {project_name}, {environment}, {executor}, {start_time}, {title}, {total}, {passed}, {failed}, {errors}, {broken}, {skipped}, {unknown}, {duration}, {report_url}, {time}

## 📊 {title}

---

### 📋 项目信息

| 项目 | 值 |
|------|------|
| 项目名称 | {project_name} |
| 运行环境 | {environment} |
| 执行人 | {executor} |
| 开始时间 | {start_time} |

---

### ✅ 测试结果概览

| 指标 | 数量 |
|------|------|
| 📊 用例总数 | {total} |
| ✅ 通过 | {passed} |
| ❌ 失败 | {failed} |
| ⚠️ 错误 | {errors} |
| 💥 中断 | {broken} |
| ⏭️ 跳过 | {skipped} |
| ❓ 未知 | {unknown} |
| ⏱️ 耗时 | {duration} |

---

### 📈 成功率

**通过率**: {pass_rate}%

---

### 🔗 相关链接

- 📄 [查看详细报告]({report_url})
- 🕐 结束时间: {time}

---

> 💡 提示：点击链接查看完整的测试报告详情
