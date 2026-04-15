# -*- coding: utf-8 -*-
# -----------------------------
# @Author    : 影子
# @Time      : 2025/3/12 15:11
# @Software  : PyCharm
# @FileName  : runner.py
# -----------------------------
import unittest
import pytest
import os
from pathlib import Path
from config.config import config
from common.log import log
from push.push_manager import push_manager


class Runner:
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent
        self.test_cases_dir = self.base_dir / "test_cases"
        self.reports_dir = self.base_dir / "reports"
        if not os.path.exists(self.reports_dir):
            os.makedirs(self.reports_dir)
        self.thread_count = config.get('thread_count', 1)

    def run_with_unittest(self):
        # 记录开始时间
        push_manager.set_start_time()
        
        log.info("使用unittest运行测试")
        test_loader = unittest.TestLoader()
        test_suite = test_loader.discover(str(self.test_cases_dir))

        # 读取报告配置
        reports_config = config.get('reports', {})
        enable_allure = reports_config.get('allure', False)
        enable_html = reports_config.get('html', False)
        
        # 如果启用了 Allure，在开始前清除旧的 Allure 数据
        if enable_allure:
            allure_dir = self.reports_dir / "allure-results"
            if os.path.exists(allure_dir):
                import shutil
                log.info(f"清除旧的 Allure 结果数据: {allure_dir}")
                try:
                    shutil.rmtree(allure_dir)
                except Exception as e:
                    log.warning(f"清除 Allure 目录失败: {e}，将覆盖写入")
            os.makedirs(allure_dir, exist_ok=True)

        
        # 如果启用了 HTML 报告，使用 XTestRunner 生成
        if enable_html:
            html_dir = self.reports_dir / "html"
            if not os.path.exists(html_dir):
                os.makedirs(html_dir)

            # 读取 XTestRunner 配置
            xtestrunner_config = reports_config.get('xtestrunner', {})
            # 从 project 配置中获取标题
            project_config = config.get('project', {})
            title = project_config.get('title', "API Automated Test Report")
            description = xtestrunner_config.get('description', "Unittest执行引擎测试报告")
            language = xtestrunner_config.get('language', "zh-CN")
            retry = xtestrunner_config.get('retry', 0)
            tester = project_config.get('executor', "自动触发")

            from XTestRunner import HTMLTestRunner
            
            # 修复 XTestRunner 的编码问题：使用二进制模式
            import io
            report_file = html_dir / "report.html"
            
            runner = HTMLTestRunner(
                stream=open(report_file, 'wb'),  # 使用二进制模式
                title=title,
                description=description,
                language=language,
                rerun=retry,
                tester=tester
            )

            # 运行测试
            result = runner.run(test_suite)
            print(f"测试结果:{result}")
            
            # 从 HTML 报告中提取准确的测试结果
            # XTestRunner 的 result 对象可能不准确，但 HTML 报告是准确的
            try:
                with open(report_file, 'r', encoding='utf-8') as f:
                    html_content = f.read()
                
                # 使用正则表达式从 HTML 中提取数据
                import re
                
                # 提取通过数量
                passed_match = re.search(r'id="p_number"[^>]*>(\d+)<', html_content)
                passed = int(passed_match.group(1)) if passed_match else 0
                
                # 提取错误数量
                error_match = re.search(r'id="e_number"[^>]*>(\d+)<', html_content)
                errors_count = int(error_match.group(1)) if error_match else 0
                
                # 提取失败数量（如果有）
                failed_match = re.search(r'id="f_number"[^>]*>(\d+)<', html_content)
                failed_count = int(failed_match.group(1)) if failed_match else 0
                
                # 提取跳过数量（如果有）
                skipped_match = re.search(r'id="s_number"[^>]*>(\d+)<', html_content)
                skipped_count = int(skipped_match.group(1)) if skipped_match else 0
                
                # 总数 = 通过 + 失败 + 错误 + 跳过
                total = passed + failed_count + errors_count + skipped_count
                
                log.info(f"从 HTML 报告提取结果: total={total}, passed={passed}, failed={failed_count}, errors={errors_count}, skipped={skipped_count}")
                
                # 构造虚拟的 failures/errors/skipped 列表（用于 Allure）
                failures = [(f"Test_{i}", "Failed") for i in range(failed_count)]
                errors = [(f"Test_{i}", "Error") for i in range(errors_count)]
                skipped = [(f"Test_{i}", "Skipped") for i in range(skipped_count)]
                
            except Exception as e:
                log.warning(f"无法从 HTML 报告提取数据: {e}，使用 XTestRunner result 对象")
                # 降级方案：使用 XTestRunner 的 result 对象
                failures = getattr(result, 'failures', [])
                errors = getattr(result, 'errors', [])
                skipped = getattr(result, 'skipped', [])
                tests_run_from_attr = getattr(result, 'testsRun', 0)
                
                if tests_run_from_attr == 0 and (len(failures) > 0 or len(errors) > 0 or len(skipped) > 0):
                    total = len(failures) + len(errors) + len(skipped)
                    passed = 0
                else:
                    total = tests_run_from_attr
                    passed = max(0, total - len(failures) - len(errors) - len(skipped))
            
            # 如果同时启用了 Allure，生成 Allure 报告
            if enable_allure:
                # 为 Allure 构造一个临时的 result 对象
                class TempResult:
                    def __init__(self):
                        self.testsRun = total
                        self.failures = failures
                        self.errors = errors
                        self.skipped = skipped
                
                temp_result = TempResult()
                self._generate_allure_from_unittest(temp_result)
            
            # 打印详细日志
            log.info("=" * 60)
            log.info("测试结果详情 (XTestRunner):")
            log.info(f"  使用的 total: {total}")
            log.info(f"  passed: {passed}")
            log.info(f"  failed: {len(failures)}")
            log.info(f"  errors: {len(errors)}")
            log.info(f"  skipped: {len(skipped)}")
            log.info("=" * 60)
            
            result_dict = {
                'total': total,
                'passed': passed,
                'failed': len(failures),
                'errors': len(errors),
                'skipped': len(skipped),
                'broken': 0,
                'unknown': 0,
                'duration': 'N/A'
            }
        else:
            # 如果没有启用 HTML 报告，直接运行测试
            text_runner = unittest.TextTestRunner(verbosity=2)
            result = text_runner.run(test_suite)
            
            # 如果启用了 Allure，生成 Allure 报告（数据已在方法开始时清理）
            if enable_allure:
                self._generate_allure_from_unittest(result)
            
            # 提取测试结果数据
            result_dict = {
                'total': getattr(result, 'testsRun', 0),
                'passed': max(0, getattr(result, 'testsRun', 0) - len(getattr(result, 'failures', [])) - len(getattr(result, 'errors', [])) - len(getattr(result, 'skipped', []))),
                'failed': len(getattr(result, 'failures', [])),
                'errors': len(getattr(result, 'errors', [])),
                'skipped': len(getattr(result, 'skipped', [])),
                'broken': 0,
                'unknown': 0,
                'duration': 'N/A'
            }

        self._send_notification(result=result_dict)
        return result

    def run_with_pytest(self):
        # 记录开始时间
        push_manager.set_start_time()
        
        log.info("使用pytest运行测试")
        
        # 读取报告配置
        reports_config = config.get('reports', {})
        enable_allure = reports_config.get('allure', False)
        enable_html = reports_config.get('html', False)

        pytest_args = [
            str(self.test_cases_dir),
            "-v"
        ]

        # 如果启用了 Allure，添加 Allure 参数
        if enable_allure:
            allure_dir = self.reports_dir / "allure-results"
            # 清除旧的 Allure 结果数据
            if os.path.exists(allure_dir):
                import shutil
                log.info(f"清除旧的 Allure 结果数据: {allure_dir}")
                try:
                    shutil.rmtree(allure_dir)
                except Exception as e:
                    log.warning(f"清除 Allure 目录失败: {e}，将覆盖写入")
            os.makedirs(allure_dir, exist_ok=True)
            pytest_args.extend(["--alluredir", str(allure_dir)])

        # 如果启用了 HTML 报告，添加 HTML 参数
        if enable_html:
            html_dir = self.reports_dir / "html"
            if not os.path.exists(html_dir):
                os.makedirs(html_dir)

            # 读取 pytest-xhtml 配置
            pytest_xhtml_config = reports_config.get('pytest_xhtml', {})
            css_files = pytest_xhtml_config.get('css', [])

            pytest_args.extend(["--html", str(html_dir / "report.html")])
            for css in css_files:
                pytest_args.extend(["--css", css])

        if self.thread_count > 1:
            pytest_args.extend([f"-n", str(self.thread_count)])

        result = pytest.main(pytest_args)

        # 从 pytest HTML 报告中提取结果
        pytest_total = 0
        pytest_passed = 0
        pytest_failed = 0
        pytest_errors = 0
        pytest_skipped = 0
        pytest_xfailed = 0
        pytest_xpassed = 0
        
        if enable_html:
            try:
                html_dir = self.reports_dir / "html"
                pytest_report_file = html_dir / "report.html"
                if pytest_report_file.exists():
                    with open(pytest_report_file, 'r', encoding='utf-8') as f:
                        html_content = f.read()
                    
                    import re
                    
                    # pytest-xhtml 报告格式: <span class="passed d-block">Passed</span>\n                <span class="h3">\n                  31\n                </span>
                    # 提取 passed (需要处理换行符)
                    passed_section = re.search(r'passed d-block.*?h3.*?([\d]+)', html_content, re.DOTALL)
                    if passed_section:
                        pytest_passed = int(passed_section.group(1))
                        log.info(f"提取到 passed: {pytest_passed}")
                    else:
                        log.warning("未找到 passed 数据")
                    
                    # 提取 failed
                    failed_section = re.search(r'failed d-block.*?h3.*?([\d]+)', html_content, re.DOTALL)
                    if failed_section:
                        pytest_failed = int(failed_section.group(1))
                        log.info(f"提取到 failed: {pytest_failed}")
                    else:
                        log.warning("未找到 failed 数据")
                    
                    # 提取 errors
                    error_section = re.search(r'error d-block.*?h3.*?([\d]+)', html_content, re.DOTALL)
                    if error_section:
                        pytest_errors = int(error_section.group(1))
                        log.info(f"提取到 errors: {pytest_errors}")
                    else:
                        log.warning("未找到 error 数据")
                    
                    # 提取 skipped
                    skipped_section = re.search(r'skipped d-block.*?h3.*?([\d]+)', html_content, re.DOTALL)
                    if skipped_section:
                        pytest_skipped = int(skipped_section.group(1))
                        log.info(f"提取到 skipped: {pytest_skipped}")
                    else:
                        log.warning("未找到 skipped 数据")
                    
                    # 提取 xfailed (预期失败)
                    xfailed_section = re.search(r'xfailed d-block.*?h3.*?([\d]+)', html_content, re.DOTALL)
                    if xfailed_section:
                        pytest_xfailed = int(xfailed_section.group(1))
                        log.info(f"提取到 xfailed: {pytest_xfailed}")
                    
                    # 提取 xpassed (预期失败但实际通过)
                    xpassed_section = re.search(r'xpassed d-block.*?h3.*?([\d]+)', html_content, re.DOTALL)
                    if xpassed_section:
                        pytest_xpassed = int(xpassed_section.group(1))
                        log.info(f"提取到 xpassed: {pytest_xpassed}")
                    
                    # 总数 = passed + failed + errors + skipped + xfailed + xpassed
                    pytest_total = pytest_passed + pytest_failed + pytest_errors + pytest_skipped + pytest_xfailed + pytest_xpassed
                    
                    log.info(f"从 pytest HTML 报告提取结果: total={pytest_total}, passed={pytest_passed}, failed={pytest_failed}, errors={pytest_errors}, skipped={pytest_skipped}, xfailed={pytest_xfailed}, xpassed={pytest_xpassed}")
                else:
                    log.warning(f"pytest HTML 报告不存在: {pytest_report_file}")
            except Exception as e:
                log.error(f"无法从 pytest HTML 报告提取数据: {e}", exc_info=True)
        else:
            log.warning("未启用 HTML 报告，无法提取 pytest 结果")
        
        # 构造结果字典
        result_dict = {
            'total': pytest_total,
            'passed': pytest_passed + pytest_xpassed,  # xpassed 也算通过
            'failed': pytest_failed,
            'errors': pytest_errors,
            'skipped': pytest_skipped,
            'broken': pytest_xfailed,  # xfailed 算作 broken
            'unknown': 0,
            'duration': 'N/A'  # 会在推送管理器中计算
        }

        # 如果启用了 Allure，生成 Allure HTML 报告
        if enable_allure:
            self._generate_allure_report()

        self._send_notification(result=result_dict)
        return result_dict

    def run_mixed(self):
        """
        混合模式：同时运行 unittest 和 pytest 测试
        先运行 unittest，再运行 pytest，合并结果
        """
        # 记录开始时间
        push_manager.set_start_time()
        
        log.info("=" * 60)
        log.info("使用混合模式运行测试 (unittest + pytest)")
        log.info("=" * 60)
        
        # 读取报告配置
        reports_config = config.get('reports', {})
        enable_allure = reports_config.get('allure', False)
        enable_html = reports_config.get('html', False)
        
        # 如果启用了 Allure，在开始前清除旧的 Allure 数据
        if enable_allure:
            allure_dir = self.reports_dir / "allure-results"
            if os.path.exists(allure_dir):
                import shutil
                log.info(f"清除旧的 Allure 结果数据: {allure_dir}")
                try:
                    shutil.rmtree(allure_dir)
                except Exception as e:
                    log.warning(f"清除 Allure 目录失败: {e}，将覆盖写入")
            os.makedirs(allure_dir, exist_ok=True)
        
        # 初始化合并的测试结果
        merged_result = {
            'total': 0,
            'passed': 0,
            'failed': 0,
            'errors': 0,
            'skipped': 0,
            'broken': 0,
            'unknown': 0,
            'duration': 'N/A'
        }
        
        # ========== 第一阶段：运行 unittest ==========
        log.info(">>> 阶段 1/2: 运行 unittest 测试")
        log.info("-" * 60)
        
        test_loader = unittest.TestLoader()
        test_suite = test_loader.discover(str(self.test_cases_dir))
        
        # 检查是否有 unittest 测试
        def count_tests(suite):
            count = 0
            for item in suite:
                if isinstance(item, unittest.TestSuite):
                    count += count_tests(item)
                else:
                    count += 1
            return count
        
        unittest_count = count_tests(test_suite)
        
        if unittest_count > 0:
            # 如果启用了 HTML 报告，使用 XTestRunner 生成
            if enable_html:
                html_dir = self.reports_dir / "html"
                if not os.path.exists(html_dir):
                    os.makedirs(html_dir)

                xtestrunner_config = reports_config.get('xtestrunner', {})
                # 从 project 配置中获取标题
                project_config = config.get('project', {})
                title = project_config.get('title', "API Automated Test Report")
                description = xtestrunner_config.get('description', "Unittest执行引擎报告")
                language = xtestrunner_config.get('language', "zh-CN")
                retry = xtestrunner_config.get('retry', 0)
                tester = project_config.get('executor', "自动触发")

                from XTestRunner import HTMLTestRunner
                
                report_file = html_dir / "report_unittest.html"
                
                runner = HTMLTestRunner(
                    stream=open(report_file, 'wb'),
                    title=title,
                    description=description,
                    language=language,
                    rerun=retry,
                    tester=tester
                )

                result = runner.run(test_suite)
                print(f">>> 测试结果:{result}")
                # 从 HTML 报告中提取准确的测试结果
                try:
                    with open(report_file, 'r', encoding='utf-8') as f:
                        html_content = f.read()
                    
                    import re
                    
                    # 提取通过数量
                    passed_match = re.search(r'id="p_number"[^>]*>(\d+)<', html_content)
                    passed = int(passed_match.group(1)) if passed_match else 0
                    
                    # 提取错误数量
                    error_match = re.search(r'id="e_number"[^>]*>(\d+)<', html_content)
                    errors_count = int(error_match.group(1)) if error_match else 0
                    
                    # 提取失败数量
                    failed_match = re.search(r'id="f_number"[^>]*>(\d+)<', html_content)
                    failed_count = int(failed_match.group(1)) if failed_match else 0
                    
                    # 提取跳过数量
                    skipped_match = re.search(r'id="s_number"[^>]*>(\d+)<', html_content)
                    skipped_count = int(skipped_match.group(1)) if skipped_match else 0
                    
                    total = passed + failed_count + errors_count + skipped_count
                    
                    log.info(f"从 unittest HTML 报告提取结果: total={total}, passed={passed}, failed={failed_count}, errors={errors_count}, skipped={skipped_count}")
                    
                    # 构造虚拟列表用于后续处理
                    failures = [(f"Test_{i}", "Failed") for i in range(failed_count)]
                    errors = [(f"Test_{i}", "Error") for i in range(errors_count)]
                    skipped = [(f"Test_{i}", "Skipped") for i in range(skipped_count)]
                    
                except Exception as e:
                    log.warning(f"无法从 unittest HTML 报告提取数据: {e}，使用 XTestRunner result 对象")
                    # 降级方案
                    failures = getattr(result, 'failures', [])
                    errors = getattr(result, 'errors', [])
                    skipped = getattr(result, 'skipped', [])
                    tests_run_from_attr = getattr(result, 'testsRun', 0)
                    
                    if tests_run_from_attr == 0 and (len(failures) > 0 or len(errors) > 0 or len(skipped) > 0):
                        total = len(failures) + len(errors) + len(skipped)
                        passed = 0
                    else:
                        total = tests_run_from_attr
                        passed = max(0, total - len(failures) - len(errors) - len(skipped))
                
                log.info(f"Unittest 结果: total={total}, passed={passed}, failed={len(failures)}, errors={len(errors)}, skipped={len(skipped)}")
                
                # 如果同时启用了 Allure，生成 Allure 报告
                if enable_allure:
                    # 构造临时的 result 对象用于 Allure 生成
                    class TempResult:
                        def __init__(self):
                            self.testsRun = total
                            self.failures = failures
                            self.errors = errors
                            self.skipped = skipped
                    
                    temp_result = TempResult()
                    self._generate_allure_from_unittest(temp_result)
                
                # 合并结果
                merged_result['total'] += total
                merged_result['passed'] += passed
                merged_result['failed'] += len(failures)
                merged_result['errors'] += len(errors)
                merged_result['skipped'] += len(skipped)
            else:
                # 没有启用 HTML 报告，直接运行
                text_runner = unittest.TextTestRunner(verbosity=2)
                result = text_runner.run(test_suite)
                
                failures = result.failures
                errors = result.errors
                skipped = result.skipped
                total = result.testsRun
                passed = max(0, total - len(failures) - len(errors) - len(skipped))
                
                log.info(f"Unittest 结果: total={total}, passed={passed}, failed={len(failures)}, errors={len(errors)}, skipped={len(skipped)}")
                
                # 合并结果
                merged_result['total'] += total
                merged_result['passed'] += passed
                merged_result['failed'] += len(failures)
                merged_result['errors'] += len(errors)
                merged_result['skipped'] += len(skipped)
        else:
            log.info("未发现 unittest 测试用例，跳过")
        
        # ========== 第二阶段：运行 pytest ==========
        log.info(">>> 阶段 2/2: 运行 pytest 测试")
        log.info("-" * 60)
        
        # 实际运行 pytest
        pytest_run_args = [
            str(self.test_cases_dir),
            "-v",
            "--tb=short"  # 简短的 traceback
        ]
        
        # 如果启用了 Allure，添加 Allure 参数（不清除数据，追加到 unittest 数据后面）
        if enable_allure:
            allure_dir = self.reports_dir / "allure-results"
            os.makedirs(allure_dir, exist_ok=True)
            pytest_run_args.extend(["--alluredir", str(allure_dir)])

        # 如果启用了 HTML 报告，添加 HTML 参数
        if enable_html:
            html_dir = self.reports_dir / "html"
            if not os.path.exists(html_dir):
                os.makedirs(html_dir)

            pytest_xhtml_config = reports_config.get('pytest_xhtml', {})
            css_files = pytest_xhtml_config.get('css', [])

            pytest_run_args.extend(["--html", str(html_dir / "report_pytest.html")])
            for css in css_files:
                pytest_run_args.extend(["--css", css])

        if self.thread_count > 1:
            pytest_run_args.extend([f"-n", str(self.thread_count)])

        # 直接运行 pytest（不捕获输出，保持正常显示）
        log.info("开始执行 pytest 测试...")
        pytest_exit_code = pytest.main(pytest_run_args)
        log.info(f"Pytest 执行完成，退出码: {pytest_exit_code}")
        
        # 从 pytest HTML 报告中提取结果
        pytest_total = 0
        pytest_passed = 0
        pytest_failed = 0
        pytest_errors = 0
        pytest_skipped = 0
        pytest_xfailed = 0
        pytest_xpassed = 0
        
        if enable_html:
            try:
                pytest_report_file = html_dir / "report_pytest.html"
                if pytest_report_file.exists():
                    with open(pytest_report_file, 'r', encoding='utf-8') as f:
                        html_content = f.read()
                    
                    import re
                    
                    # pytest-xhtml 报告格式: <span class="passed d-block">Passed</span>\n                <span class="h3">\n                  31\n                </span>
                    # 提取 passed (需要处理换行符)
                    passed_section = re.search(r'passed d-block.*?h3.*?([\d]+)', html_content, re.DOTALL)
                    if passed_section:
                        pytest_passed = int(passed_section.group(1))
                    
                    # 提取 failed
                    failed_section = re.search(r'failed d-block.*?h3.*?([\d]+)', html_content, re.DOTALL)
                    if failed_section:
                        pytest_failed = int(failed_section.group(1))
                    
                    # 提取 errors
                    error_section = re.search(r'error d-block.*?h3.*?([\d]+)', html_content, re.DOTALL)
                    if error_section:
                        pytest_errors = int(error_section.group(1))
                    
                    # 提取 skipped
                    skipped_section = re.search(r'skipped d-block.*?h3.*?([\d]+)', html_content, re.DOTALL)
                    if skipped_section:
                        pytest_skipped = int(skipped_section.group(1))
                    
                    # 提取 xfailed (预期失败)
                    xfailed_section = re.search(r'xfailed d-block.*?h3.*?([\d]+)', html_content, re.DOTALL)
                    if xfailed_section:
                        pytest_xfailed = int(xfailed_section.group(1))
                    
                    # 提取 xpassed (预期失败但实际通过)
                    xpassed_section = re.search(r'xpassed d-block.*?h3.*?([\d]+)', html_content, re.DOTALL)
                    if xpassed_section:
                        pytest_xpassed = int(xpassed_section.group(1))
                    
                    # 总数 = passed + failed + errors + skipped + xfailed + xpassed
                    pytest_total = pytest_passed + pytest_failed + pytest_errors + pytest_skipped + pytest_xfailed + pytest_xpassed
                    
                    log.info(f"从 pytest HTML 报告提取结果: total={pytest_total}, passed={pytest_passed}, failed={pytest_failed}, errors={pytest_errors}, skipped={pytest_skipped}, xfailed={pytest_xfailed}, xpassed={pytest_xpassed}")
                else:
                    log.warning(f"pytest HTML 报告不存在: {pytest_report_file}")
            except Exception as e:
                log.warning(f"无法从 pytest HTML 报告提取数据: {e}")
        else:
            log.warning("未启用 HTML 报告，无法获取 pytest 精确结果")
        
        log.info(f"Pytest 结果: total={pytest_total}, passed={pytest_passed}, failed={pytest_failed}, errors={pytest_errors}, skipped={pytest_skipped}, xfailed={pytest_xfailed}, xpassed={pytest_xpassed}")
        
        # 合并 pytest 结果（注意：xpassed 计入 passed，xfailed 计入 broken）
        merged_result['total'] += pytest_total
        merged_result['passed'] += pytest_passed + pytest_xpassed  # xpassed 也算通过
        merged_result['failed'] += pytest_failed
        merged_result['errors'] += pytest_errors
        merged_result['skipped'] += pytest_skipped
        merged_result['broken'] += pytest_xfailed  # xfailed 算作 broken
        
        # 如果启用了 Allure，生成 Allure HTML 报告
        if enable_allure:
            self._generate_allure_report()
        
        # 打印合并后的结果
        log.info("=" * 60)
        log.info("混合模式测试结果汇总:")
        log.info(f"  总用例数: {merged_result['total']}")
        log.info(f"  通过: {merged_result['passed']}")
        log.info(f"  失败: {merged_result['failed']}")
        log.info(f"  错误: {merged_result['errors']}")
        log.info(f"  跳过: {merged_result['skipped']}")
        log.info(f"  中断: {merged_result['broken']}")
        
        # 计算通过率
        executed = merged_result['total'] - merged_result['skipped']
        pass_rate = round((merged_result['passed'] / executed * 100), 2) if executed > 0 else 0
        log.info(f"  通过率: {pass_rate}%")
        log.info("=" * 60)
        
        # 发送通知
        self._send_notification(result=merged_result)
        
        return merged_result

    def _generate_allure_from_unittest(self, test_result):
        """
        从 unittest/XTestRunner 测试结果生成 Allure 报告
        
        :param test_result: XTestRunner 的测试结果对象
        """
        import json
        import time
        import uuid
        from datetime import datetime
        
        log.info("从 unittest 结果生成 Allure 报告")
        allure_results = self.reports_dir / "allure-results"
        if not os.path.exists(allure_results):
            os.makedirs(allure_results)
        
        # 解析测试结果
        total = getattr(test_result, 'testsRun', 0)
        failures = getattr(test_result, 'failures', [])
        errors = getattr(test_result, 'errors', [])
        skipped = getattr(test_result, 'skipped', [])
        passed = max(0, total - len(failures) - len(errors) - len(skipped))
        
        # 为每个测试用例生成 Allure result JSON
        test_index = 0
        
        # 处理通过的测试
        # 由于 XTestRunner 不直接提供通过的测试列表，我们只能统计数量
        for i in range(passed):
            test_uuid = str(uuid.uuid4())
            result_data = {
                "uuid": test_uuid,
                "historyId": f"test_passed_{i}",
                "testCaseId": f"unittest_passed_{i}",
                "fullName": f"unittest.test_passed_{i}",
                "labels": [
                    {"name": "suite", "value": "Unittest Tests"},
                    {"name": "testClass", "value": "PassedTests"},
                    {"name": "package", "value": "unittest"},
                    {"name": "framework", "value": "unittest"},
                    {"name": "language", "value": "python"}
                ],
                "name": f"Passed Test #{i+1}",
                "status": "passed",
                "stage": "finished",
                "start": int(time.time() * 1000) - 1000,
                "stop": int(time.time() * 1000)
            }
            
            result_file = allure_results / f"{test_uuid}-result.json"
            with open(result_file, 'w', encoding='utf-8') as f:
                json.dump(result_data, f, ensure_ascii=False, indent=2)
        
        # 处理失败的测试
        for i, (test_name, error_msg) in enumerate(failures):
            test_uuid = str(uuid.uuid4())
            result_data = {
                "uuid": test_uuid,
                "historyId": f"test_failed_{i}",
                "testCaseId": f"unittest_failed_{i}",
                "fullName": str(test_name),
                "labels": [
                    {"name": "suite", "value": "Unittest Tests"},
                    {"name": "testClass", "value": "FailedTests"},
                    {"name": "package", "value": "unittest"},
                    {"name": "framework", "value": "unittest"},
                    {"name": "language", "value": "python"}
                ],
                "name": str(test_name).split('.')[-1] if '.' in str(test_name) else str(test_name),
                "status": "failed",
                "stage": "finished",
                "statusDetails": {
                    "message": "Assertion Failed",
                    "trace": str(error_msg)[:5000]  # 限制长度
                },
                "start": int(time.time() * 1000) - 1000,
                "stop": int(time.time() * 1000)
            }
            
            result_file = allure_results / f"{test_uuid}-result.json"
            with open(result_file, 'w', encoding='utf-8') as f:
                json.dump(result_data, f, ensure_ascii=False, indent=2)
        
        # 处理错误的测试
        for i, (test_name, error_msg) in enumerate(errors):
            test_uuid = str(uuid.uuid4())
            result_data = {
                "uuid": test_uuid,
                "historyId": f"test_error_{i}",
                "testCaseId": f"unittest_error_{i}",
                "fullName": str(test_name),
                "labels": [
                    {"name": "suite", "value": "Unittest Tests"},
                    {"name": "testClass", "value": "ErrorTests"},
                    {"name": "package", "value": "unittest"},
                    {"name": "framework", "value": "unittest"},
                    {"name": "language", "value": "python"}
                ],
                "name": str(test_name).split('.')[-1] if '.' in str(test_name) else str(test_name),
                "status": "broken",
                "stage": "finished",
                "statusDetails": {
                    "message": "Test Error",
                    "trace": str(error_msg)[:5000]
                },
                "start": int(time.time() * 1000) - 1000,
                "stop": int(time.time() * 1000)
            }
            
            result_file = allure_results / f"{test_uuid}-result.json"
            with open(result_file, 'w', encoding='utf-8') as f:
                json.dump(result_data, f, ensure_ascii=False, indent=2)
        
        # 处理跳过的测试
        for i, (test_name, reason) in enumerate(skipped):
            test_uuid = str(uuid.uuid4())
            result_data = {
                "uuid": test_uuid,
                "historyId": f"test_skipped_{i}",
                "testCaseId": f"unittest_skipped_{i}",
                "fullName": str(test_name),
                "labels": [
                    {"name": "suite", "value": "Unittest Tests"},
                    {"name": "testClass", "value": "SkippedTests"},
                    {"name": "package", "value": "unittest"},
                    {"name": "framework", "value": "unittest"},
                    {"name": "language", "value": "python"}
                ],
                "name": str(test_name).split('.')[-1] if '.' in str(test_name) else str(test_name),
                "status": "skipped",
                "stage": "pending",
                "statusDetails": {
                    "message": str(reason) if reason else "Skipped"
                },
                "start": int(time.time() * 1000) - 1000,
                "stop": int(time.time() * 1000)
            }
            
            result_file = allure_results / f"{test_uuid}-result.json"
            with open(result_file, 'w', encoding='utf-8') as f:
                json.dump(result_data, f, ensure_ascii=False, indent=2)
        
        log.info(f"Allure 结果文件生成于: {allure_results}")
        log.info(f"  - 通过: {passed}, 失败: {len(failures)}, 错误: {len(errors)}, 跳过: {len(skipped)}")
        
        # 生成 Allure HTML 报告并打开
        self._generate_allure_report()
    
    def _generate_allure_report(self):
        log.info("生成Allure报告")
        allure_results = self.reports_dir / "allure-results"
        allure_report = self.reports_dir / "allure-report"

        import subprocess
        import os

        # 优先使用项目自带的 Allure 安装包
        base_dir = Path(__file__).parent.parent
        allure_bin_dir = base_dir / "runner" / "allure" / "bin"
        
        # 根据操作系统选择对应的可执行文件
        if os.name == 'nt':  # Windows
            allure_cmd = allure_bin_dir / "allure.bat"
        else:  # Linux/Mac
            allure_cmd = allure_bin_dir / "allure"
        
        # 检查本地 Allure 是否存在
        if allure_cmd.exists():
            log.info(f"使用项目自带的Allure: {allure_cmd}")
            try:
                # 生成报告
                result = subprocess.run(
                    [str(allure_cmd), "generate", str(allure_results), "-o", str(allure_report), "--clean"],
                    check=True, capture_output=True, text=True)
                log.info(f"Allure报告生成于: {allure_report}")
                log.debug(f"Allure输出: {result.stdout}")
                
                # 自动打开报告
                log.info("正在打开Allure报告...")
                subprocess.Popen(
                    [str(allure_cmd), "open", str(allure_report)],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                log.info("Allure报告已在浏览器中打开")
            except subprocess.CalledProcessError as e:
                log.error(f"生成Allure报告失败: {e.stderr}")
            except Exception as e:
                log.error(f"生成Allure报告失败: {str(e)}")
        else:
            # 如果本地不存在，尝试从系统 PATH 查找
            import shutil
            allure_cmd = shutil.which("allure")
            if allure_cmd:
                log.info(f"在系统PATH中找到Allure命令: {allure_cmd}")
                try:
                    # 生成报告
                    result = subprocess.run(
                        [allure_cmd, "generate", str(allure_results), "-o", str(allure_report), "--clean"],
                        check=True, capture_output=True, text=True)
                    log.info(f"Allure报告生成于: {allure_report}")
                    log.debug(f"Allure输出: {result.stdout}")
                    
                    # 自动打开报告
                    log.info("正在打开Allure报告...")
                    subprocess.Popen(
                        [allure_cmd, "open", str(allure_report)],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL
                    )
                    log.info("Allure报告已在浏览器中打开")
                except subprocess.CalledProcessError as e:
                    log.error(f"生成Allure报告失败: {e.stderr}")
                except Exception as e:
                    log.error(f"生成Allure报告失败: {str(e)}")
            else:
                log.warning("找不到Allure命令。请确保 runner/allure/bin 目录存在或安装Allure到系统PATH。")
                log.info(f"Allure结果保存在: {allure_results}")
                log.info("要生成并打开报告，请运行: allure generate <allure-results> -o <allure-report> --clean && allure open <allure-report>")

    def _send_notification(self, subject=None, content=None, result=None):
        """
        发送通知
        
        :param subject: 主题（兼容旧接口）
        :param content: 内容（兼容旧接口）
        :param result: 测试结果对象
        """
        # 优先使用新的模板方式
        if result is not None:
            push_manager.send_notification(subject=subject, test_result=result)
        else:
            # 兼容旧接口
            push_manager.send_notification(subject=subject, content=content)


runner = Runner()
