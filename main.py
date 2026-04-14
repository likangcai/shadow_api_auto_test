# -*- coding: utf-8 -*-
# -----------------------------
# @Author    : 影子
# @Time      : 2025/3/12 18:13
# @Software  : PyCharm
# @FileName  : test_httpbin.py
# -----------------------------
from config.config import config
from runner.runner import runner
from common.log import log

if __name__ == "__main__":
    log.info("启动API自动化测试框架")
    test_runner = config.get('test_runner', 'pytest')
    
    if test_runner == 'unittest':
        log.info("使用 unittest 引擎")
        result = runner.run_with_unittest()
    elif test_runner == 'pytest':
        log.info("使用 pytest 引擎")
        result = runner.run_with_pytest()
    elif test_runner == 'mixed':
        log.info("使用混合模式 (unittest + pytest)")
        result = runner.run_mixed()
    else:
        log.error(f"不支持的测试引擎: {test_runner}")
        log.info("支持的引擎: unittest, pytest, mixed")
        exit(1)
    
    log.info("测试执行已完成")
