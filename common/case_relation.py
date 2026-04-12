# -*- coding: utf-8 -*-
# -----------------------------
# @Author    : 影子
# @Time      : 2025/3/10 10:51
# @Software  : PyCharm
# @FileName  : case_relation.py
# -----------------------------
class CaseRelation:
    """
    用例关系管理类
    """

    def __init__(self):
        self.variables = {}

    def set_variable(self, key, value):
        """
        设置测试用例变量

        :param key: 变量名称，作为键存储
        :param value: 变量值，需要存储的数据
        :return: None
        """
        self.variables[key] = value

    def get_variable(self, key, default=None):
        """
        获取测试用例变量的值

        :param key: 变量名称，用于查找对应的变量值
        :param default: 默认值，当变量不存在时返回此值，默认为None
        :return: 变量值，如果变量存在则返回其值，否则返回default参数指定的默认值
        """
        return self.variables.get(key, default)

    def update_variables(self, variables):
        """
        批量更新测试用例变量

        :param variables: 字典类型的变量集合，用于批量更新现有变量
        :return: None
        """
        self.variables.update(variables)

    def clear_variables(self):
        """
        清空所有测试用例变量

        :return: None
        """
        self.variables.clear()

    def get_all_variables(self):
        """
        获取所有测试用例变量的副本

        :return: 返回当前所有变量的字典副本，避免外部直接修改内部状态
        """
        return self.variables.copy()


case_relation = CaseRelation()
