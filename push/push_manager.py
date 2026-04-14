# -*- coding: utf-8 -*-
# -----------------------------
# @Author    : 影子
# @Time      : 2025/3/12 11:43
# @Software  : PyCharm
# @FileName  : push_manager.py
# -----------------------------
from config.config import config
from push.email import email_push
from push.dingtalk import dingtalk_push
from push.feishu import feishu_push
from push.wecom import wecom_push
from common.log import log
from datetime import datetime

class PushManager:
    def __init__(self):
        self.push_config = config.get('push', {})
        self.start_time = None  # 记录开始执行时间
    
    def set_start_time(self, start_time=None):
        """
        设置测试开始时间
        
        :param start_time: datetime 对象，如果为 None 则使用当前时间
        """
        self.start_time = start_time or datetime.now()
        log.debug(f"测试开始时间设置为: {self.start_time}")
    
    def _calculate_duration(self):
        """
        计算测试执行耗时
        
        :return: 格式化的耗时字符串，如 "1m 30s" 或 "45s"
        """
        if not self.start_time:
            return 'N/A'
        
        end_time = datetime.now()
        duration_seconds = (end_time - self.start_time).total_seconds()
        
        # 格式化耗时
        if duration_seconds < 60:
            # 小于1分钟，显示秒
            return f"{int(duration_seconds)}s"
        elif duration_seconds < 3600:
            # 小于1小时，显示分+秒
            minutes = int(duration_seconds // 60)
            seconds = int(duration_seconds % 60)
            return f"{minutes}m {seconds}s"
        else:
            # 大于1小时，显示时+分+秒
            hours = int(duration_seconds // 3600)
            minutes = int((duration_seconds % 3600) // 60)
            seconds = int(duration_seconds % 60)
            return f"{hours}h {minutes}m {seconds}s"
    
    def send_notification(self, subject=None, content=None, test_result=None):
        """
        发送通知
        
        :param subject: 主题（兼容旧接口）
        :param content: 内容（兼容旧接口）
        :param test_result: 测试结果字典，包含 total, passed, failed, errors, duration 等
        """
        # 如果提供了 test_result，使用模板渲染
        if test_result:
            variables = self._prepare_variables(test_result, subject)
            
            if self.push_config.get('email', False):
                # 邮件仍使用 HTML 格式
                html_content = self._generate_html_content(variables)
                email_push.send(variables['title'], html_content)
            
            if self.push_config.get('dingtalk', False):
                dingtalk_push.send(variables=variables)
            
            if self.push_config.get('feishu', False):
                feishu_push.send(variables=variables)
            
            if self.push_config.get('wecom', False):
                wecom_push.send(variables=variables)
        else:
            # 兼容旧接口，直接发送文本
            message = f"{subject}\n\n{content}" if subject and content else (subject or content)
            
            if self.push_config.get('email', False):
                email_push.send(subject or '', content or '')
            
            if self.push_config.get('dingtalk', False):
                dingtalk_push.send(message)
            
            if self.push_config.get('feishu', False):
                feishu_push.send(message)
            
            if self.push_config.get('wecom', False):
                wecom_push.send(message)
    
    def _prepare_variables(self, test_result, subject=None):
        """
        准备模板变量
        
        :param test_result: 测试结果对象或字典
        :param subject: 可选的主题
        :return: 变量字典
        """
        import unittest
        
        # 打印接收到的原始数据
        log.info("=" * 60)
        log.info(f"推送管理器接收到 test_result 类型: {type(test_result)}")
        if isinstance(test_result, dict):
            log.info(f"test_result 内容: {test_result}")
        else:
            log.info(f"test_result 属性: testsRun={getattr(test_result, 'testsRun', 'N/A')}, "
                    f"failures={len(getattr(test_result, 'failures', []))}, "
                    f"errors={len(getattr(test_result, 'errors', []))}, "
                    f"skipped={len(getattr(test_result, 'skipped', []))}")
        
        # 解析测试结果
        if isinstance(test_result, unittest.TestResult):
            # 标准 unittest TestResult
            total = test_result.testsRun
            failed = len(test_result.failures)
            errors = len(test_result.errors)
            skipped = len(test_result.skipped)
            passed = total - failed - errors - skipped
            broken = 0
            unknown = 0
            duration = self._calculate_duration()
            log.info("解析方式: unittest.TestResult")
        elif hasattr(test_result, 'testsRun'):
            # XTestRunner 或其他自定义结果对象
            total = getattr(test_result, 'testsRun', 0)
            failed = len(getattr(test_result, 'failures', []))
            errors = len(getattr(test_result, 'errors', []))
            skipped = len(getattr(test_result, 'skipped', []))
            passed = total - failed - errors - skipped
            broken = 0
            unknown = 0
            duration = self._calculate_duration()
            log.info("解析方式: 自定义结果对象 (hasattr testsRun)")
        elif isinstance(test_result, dict):
            # 字典格式（如 pytest 或手动构造）
            total = test_result.get('total', 0)
            passed = test_result.get('passed', 0)
            failed = test_result.get('failed', 0)
            errors = test_result.get('errors', 0)
            skipped = test_result.get('skipped', 0)
            broken = test_result.get('broken', 0)
            unknown = test_result.get('unknown', 0)
            # 如果字典中已经有 duration，使用它；否则计算
            duration = test_result.get('duration', None)
            if duration is None or duration == 'N/A':
                duration = self._calculate_duration()
            log.info("解析方式: dict 字典")
        else:
            # 其他类型（如 pytest 的退出码）
            total = passed = failed = errors = skipped = broken = unknown = 0
            duration = self._calculate_duration()
            log.info("解析方式: 未知类型，使用默认值")
        
        # 确保数值不为负数
        passed = max(0, passed)
        total = max(0, total)
        
        # 计算通过率（基于执行的用例数，不包括跳过和未知的）
        executed = total - skipped - unknown
        pass_rate = round((passed / executed * 100), 2) if executed > 0 else 0
        
        # 打印解析后的数据
        log.info("解析后的测试结果:")
        log.info(f"  total: {total}")
        log.info(f"  passed: {passed}")
        log.info(f"  failed: {failed}")
        log.info(f"  errors: {errors}")
        log.info(f"  skipped: {skipped}")
        log.info(f"  broken: {broken}")
        log.info(f"  unknown: {unknown}")
        log.info(f"  pass_rate: {pass_rate}%")
        log.info("=" * 60)
        
        # 获取报告 URL（从配置文件读取）
        report_config = config.get('reports', {})
        report_url = report_config.get('report_url', '')
        
        # 如果配置文件中没有定义，则使用默认值
        if not report_url:
            base_url = config.get('base_url', '')
            if base_url:
                report_url = f"{base_url}/reports/html/report.html"
            else:
                report_url = './reports/html/report.html'
        
        # 获取项目配置信息
        project_config = config.get('project', {})
        project_name = project_config.get('name', 'API自动化测试项目')
        environment = project_config.get('environment', '测试环境')
        executor = project_config.get('executor', '').strip()
        
        # 如果执行人为空，则显示“自动触发”
        if not executor:
            executor = '🤖 自动触发'
        
        # 获取开始执行时间
        if self.start_time:
            start_time_str = self.start_time.strftime('%Y-%m-%d %H:%M:%S')
        else:
            start_time_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        return {
            'project_name': project_name,
            'environment': environment,
            'executor': executor,
            'start_time': start_time_str,
            'title': subject or 'API自动化测试报告',
            'total': total,
            'passed': passed,
            'failed': failed,
            'errors': errors,
            'broken': broken,
            'skipped': skipped,
            'unknown': unknown,
            'duration': duration,
            'pass_rate': pass_rate,
            'report_url': report_url,
            'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def _generate_html_content(self, variables):
        """
        生成 HTML 格式的邮件内容
        
        :param variables: 变量字典
        :return: HTML 字符串
        """
        # 构建测试结果行（只显示非零值）
        result_rows = [
            f"<tr><td>📊 用例总数</td><td>{variables['total']}</td></tr>",
            f"<tr><td>✅ 通过</td><td>{variables['passed']}</td></tr>",
        ]
        
        if variables.get('failed', 0) > 0:
            result_rows.append(f"<tr><td>❌ 失败</td><td>{variables['failed']}</td></tr>")
        
        if variables.get('errors', 0) > 0:
            result_rows.append(f"<tr><td>⚠️ 错误</td><td>{variables['errors']}</td></tr>")
        
        if variables.get('broken', 0) > 0:
            result_rows.append(f"<tr><td>💥 中断</td><td>{variables['broken']}</td></tr>")
        
        if variables.get('skipped', 0) > 0:
            result_rows.append(f"<tr><td>⏭️ 跳过</td><td>{variables['skipped']}</td></tr>")
        
        if variables.get('unknown', 0) > 0:
            result_rows.append(f"<tr><td>❓ 未知</td><td>{variables['unknown']}</td></tr>")
        
        result_rows.append(f"<tr><td>📈 通过率</td><td>{variables['pass_rate']}%</td></tr>")
        result_rows.append(f"<tr><td>⏱️ 耗时</td><td>{variables['duration']}</td></tr>")
        
        return f"""
        <h2>{variables['title']}</h2>
        
        <h3>📋 项目信息</h3>
        <table border="1" cellpadding="5" cellspacing="0">
            <tr><th>项目</th><th>值</th></tr>
            <tr><td>项目名称</td><td>{variables.get('project_name', 'N/A')}</td></tr>
            <tr><td>运行环境</td><td>{variables.get('environment', 'N/A')}</td></tr>
            <tr><td>执行人</td><td>{variables.get('executor', 'N/A')}</td></tr>
            <tr><td>开始时间</td><td>{variables.get('start_time', 'N/A')}</td></tr>
        </table>
        
        <h3>✅ 测试结果概览</h3>
        <table border="1" cellpadding="5" cellspacing="0">
            <tr><th>指标</th><th>数量</th></tr>
            {''.join(result_rows)}
        </table>
        
        <p><strong>执行时间</strong>: {variables['time']}</p>
        <p><a href="{variables['report_url']}">查看详细报告</a></p>
        """

push_manager = PushManager()
