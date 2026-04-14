# -*- coding: utf-8 -*-
# -----------------------------
# @Author    : 影子
# @Time      : 2026/4/14 12:00
# @Software  : PyCharm
# @FileName  : mock_helper.py
# -----------------------------
"""
Mock 服务辅助工具
提供便捷的函数来获取 Mock 服务器 URL 和构建完整的 API 路径
"""
from common.mock import mock_server


def get_mock_url(path=''):
    """
    获取 Mock 服务器的完整 URL
    
    :param path: API 路径，例如 '/api/users'
    :return: 完整的 URL，例如 'http://localhost:8899/api/users'
    
    示例:
        >>> get_mock_url('/api/users')
        'http://localhost:8899/api/users'
        
        >>> get_mock_url()
        'http://localhost:8899'
    """
    base_url = mock_server.get_base_url()
    if path:
        # 确保路径以 / 开头
        if not path.startswith('/'):
            path = '/' + path
        return f"{base_url}{path}"
    return base_url


def mock_get(path, **kwargs):
    """
    向 Mock 服务器发送 GET 请求的便捷函数
    
    :param path: API 路径
    :param kwargs: 其他请求参数
    :return: httpx.Response 对象
    
    示例:
        >>> from common.mock_helper import mock_get
        >>> response = mock_get('/api/users')
    """
    import httpx
    url = get_mock_url(path)
    return httpx.get(url, **kwargs)


def mock_post(path, **kwargs):
    """
    向 Mock 服务器发送 POST 请求的便捷函数
    
    :param path: API 路径
    :param kwargs: 其他请求参数（如 json, data 等）
    :return: httpx.Response 对象
    
    示例:
        >>> from common.mock_helper import mock_post
        >>> response = mock_post('/api/users', json={'name': 'Alice'})
    """
    import httpx
    url = get_mock_url(path)
    return httpx.post(url, **kwargs)


def mock_put(path, **kwargs):
    """
    向 Mock 服务器发送 PUT 请求的便捷函数
    
    :param path: API 路径
    :param kwargs: 其他请求参数
    :return: httpx.Response 对象
    """
    import httpx
    url = get_mock_url(path)
    return httpx.put(url, **kwargs)


def mock_delete(path, **kwargs):
    """
    向 Mock 服务器发送 DELETE 请求的便捷函数
    
    :param path: API 路径
    :param kwargs: 其他请求参数
    :return: httpx.Response 对象
    """
    import httpx
    url = get_mock_url(path)
    return httpx.delete(url, **kwargs)
