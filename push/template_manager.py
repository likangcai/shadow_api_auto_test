# -*- coding: utf-8 -*-
# -----------------------------
# @Author    : 影子
# @Time      : 2026/4/14 13:00
# @Software  : PyCharm
# @FileName  : template_manager.py
# -----------------------------
"""
消息模板管理器
支持从 Markdown 模板文件加载模板，并自动替换变量
"""
from pathlib import Path
from common.log import log


class TemplateManager:
    """消息模板管理器"""
    
    def __init__(self):
        self.template_dir = Path(__file__).parent / "templates"
        self.templates = {}
        self._load_templates()
    
    def _load_templates(self):
        """加载所有模板文件"""
        if not self.template_dir.exists():
            log.warning(f"模板目录不存在: {self.template_dir}")
            return
        
        for template_file in self.template_dir.glob("*.md"):
            template_name = template_file.stem
            try:
                with open(template_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # 移除注释行（以 # 支持变量 开头的行）
                    lines = [line for line in content.split('\n') 
                            if not line.strip().startswith('# 支持变量')]
                    # 同时移除第一个标题行（平台名称）
                    if lines and lines[0].strip().startswith('# ') and '模板' in lines[0]:
                        lines = lines[1:]
                    self.templates[template_name] = '\n'.join(lines).strip()
                log.debug(f"加载模板: {template_name}")
            except Exception as e:
                log.error(f"加载模板失败 {template_file}: {e}")
    
    def get_template(self, name):
        """
        获取模板内容
        
        :param name: 模板名称（不含 .md 扩展名）
        :return: 模板字符串，如果不存在返回 None
        """
        return self.templates.get(name)
    
    def render(self, template_name, variables):
        """
        渲染模板，替换变量
        
        :param template_name: 模板名称
        :param variables: 变量字典，例如 {'title': '测试报告', 'total': 10}
        :return: 渲染后的字符串
        """
        template = self.get_template(template_name)
        if not template:
            log.warning(f"模板不存在: {template_name}，使用默认文本格式")
            return self._default_format(variables)
        
        try:
            rendered = template
            for key, value in variables.items():
                placeholder = '{' + key + '}'
                rendered = rendered.replace(placeholder, str(value))
            return rendered
        except Exception as e:
            log.error(f"渲染模板失败: {e}")
            return self._default_format(variables)
    
    def _default_format(self, variables):
        """
        默认格式化（当模板不存在时使用）
        
        :param variables: 变量字典
        :return: 格式化的字符串
        """
        title = variables.get('title', '测试报告')
        total = variables.get('total', 0)
        passed = variables.get('passed', 0)
        failed = variables.get('failed', 0)
        errors = variables.get('errors', 0)
        duration = variables.get('duration', 'N/A')
        pass_rate = variables.get('pass_rate', 0)
        report_url = variables.get('report_url', '')
        time = variables.get('time', '')
        
        return f"""{title}

总用例数: {total}
通过: {passed}
失败: {failed}
错误: {errors}
通过率: {pass_rate}%
耗时: {duration}
执行时间: {time}
报告链接: {report_url}
"""


template_manager = TemplateManager()
