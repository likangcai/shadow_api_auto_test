# -*- coding: utf-8 -*-
# -----------------------------
# @Author    : 影子
# @Time      : 2025/3/10 13:55
# @Software  : PyCharm
# @FileName  : mock.py
# -----------------------------
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import threading
from unittest.mock import Mock, MagicMock
from common.log import log
from config.config import config


class MockHandler(BaseHTTPRequestHandler):
    """
    Mock服务器，用于模拟HTTP请求和响应
    """
    mock_responses = {}
    mock_callbacks = {}
    _lock = threading.Lock()

    @classmethod
    def set_mock_response(cls, path, response):
        """
        设置模拟的响应数据

        :param path: 请求路径
        :param response: 响应数据，可以是字典、列表或MockResponse对象
        :return: None
        """
        with cls._lock:
            if isinstance(response, dict):
                response = MockResponse(**response)
            cls.mock_responses[path] = response

    @classmethod
    def set_mock_callback(cls, path, callback):
        """
        设置动态回调函数，根据请求内容动态生成响应

        :param path: 请求路径
        :param callback: 回调函数，接收 (method, headers, body, query_params) 参数
        :return: None
        """
        with cls._lock:
            cls.mock_callbacks[path] = callback

    @classmethod
    def clear_mock_responses(cls):
        """
        清空模拟的响应数据
        :return:
        """
        with cls._lock:
            cls.mock_responses.clear()
            cls.mock_callbacks.clear()

    def _read_request_body(self):
        """
        读取请求体内容

        :return: 解析后的请求体（dict）或原始字节
        """
        content_length = int(self.headers.get('Content-Length', 0))
        if content_length > 0:
            body = self.rfile.read(content_length)
            try:
                return json.loads(body.decode('utf-8'))
            except (json.JSONDecodeError, UnicodeDecodeError):
                return body
        return None

    def _parse_query_params(self):
        """
        解析URL查询参数

        :return: 查询参数字典
        """
        from urllib.parse import urlparse, parse_qs
        parsed = urlparse(self.path)
        return {k: v[0] if len(v) == 1 else v
                for k, v in parse_qs(parsed.query).items()}

    def _get_path_without_query(self):
        """
        获取不包含查询参数的路径

        :return: 纯路径字符串
        """
        from urllib.parse import urlparse
        return urlparse(self.path).path

    def _send_mock_response(self):
        """
        发送模拟响应的公共方法
        """
        try:
            path = self._get_path_without_query()
            query_params = self._parse_query_params()
            request_body = self._read_request_body() if self.command in ['POST', 'PUT', 'PATCH'] else None

            with self._lock:
                callback = self.mock_callbacks.get(path)
                response_config = self.mock_responses.get(path)

            if callback:
                try:
                    response_data = callback(
                        method=self.command,
                        headers=dict(self.headers),
                        body=request_body,
                        query_params=query_params
                    )
                    if isinstance(response_data, MockResponse):
                        response_config = response_data
                    elif isinstance(response_data, dict):
                        response_config = MockResponse(**response_data)
                    else:
                        response_config = MockResponse(status_code=200, body=response_data)
                except Exception as e:
                    log.error(f"回调执行失败 {path}: {e}")
                    self._send_error_response(500, f"Callback error: {str(e)}")
                    return

            if response_config is not None:
                self._send_configured_response(response_config)
                log.debug(f"已发送模拟响应 {self.command} {self.path}")
            else:
                self._send_error_response(404, f"No mock response configured for path: {self.path}")
                log.warning(f"未找到的模拟响应 {self.command} {self.path}")
        except Exception as e:
            log.error(f"发送模拟响应时出错 {self.command} {self.path}: {e}")
            self._send_error_response(500, "Internal server error")

    def _send_configured_response(self, response_config):
        """
        根据配置发送响应

        :param response_config: MockResponse 对象
        """
        status_code = response_config.status_code
        headers = response_config.headers or {'Content-type': 'application/json'}
        body = response_config.body
        delay = response_config.delay

        if delay:
            time.sleep(delay)

        self.send_response(status_code)
        for header_name, header_value in headers.items():
            self.send_header(header_name, header_value)
        self.end_headers()

        if isinstance(body, (dict, list)):
            response_bytes = json.dumps(body, ensure_ascii=False).encode('utf-8')
        elif isinstance(body, str):
            response_bytes = body.encode('utf-8')
        elif isinstance(body, bytes):
            response_bytes = body
        else:
            response_bytes = json.dumps(body).encode('utf-8')

        self.wfile.write(response_bytes)

    def _send_error_response(self, status_code, error_message):
        """
        发送错误响应

        :param status_code: HTTP状态码
        :param error_message: 错误消息
        """
        try:
            self.send_response(status_code)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            error_body = json.dumps({"error": error_message}).encode('utf-8')
            self.wfile.write(error_body)
        except Exception:
            pass

    def do_GET(self):
        self._send_mock_response()

    def do_POST(self):
        self._send_mock_response()

    def do_PUT(self):
        self._send_mock_response()

    def do_DELETE(self):
        self._send_mock_response()

    def do_PATCH(self):
        self._send_mock_response()


class MockResponse:
    """
    Mock响应配置类，用于定义详细的响应行为
    """

    def __init__(self, status_code=200, body=None, headers=None, delay=0):
        """
        初始化Mock响应配置

        :param status_code: HTTP状态码，默认200
        :param body: 响应体，可以是dict、list、str或bytes
        :param headers: 响应头字典
        :param delay: 延迟响应时间（秒），用于模拟网络延迟
        """
        self.status_code = status_code
        self.body = body if body is not None else {}
        self.headers = headers or {'Content-type': 'application/json'}
        self.delay = delay


class MockServer:
    """
    Mock服务 - 基于HTTPServer的实现，适用于集成测试和API测试
    """

    def __init__(self, host=None, port=None):
        """
        初始化Mock服务器
        
        :param host: 主机地址，默认从配置文件读取
        :param port: 端口号，默认从配置文件读取（默认8899）
        """
        # 从配置文件读取默认值
        mock_config = config.get('mock_server', {})
        self.host = host or mock_config.get('host', 'localhost')
        self.port = port or mock_config.get('port', 8899)
        self.server = None
        self.thread = None

    def start(self):
        self.server = HTTPServer((self.host, self.port), MockHandler)
        self.thread = threading.Thread(target=self.server.serve_forever)
        self.thread.daemon = True
        self.thread.start()
        log.info(f"模拟服务器启动于 http://{self.host}:{self.port}")

    def stop(self):
        if self.server:
            shutdown_thread = threading.Thread(target=self.server.shutdown)
            shutdown_thread.start()
            shutdown_thread.join(timeout=5)
            self.server.server_close()
            if self.thread:
                self.thread.join(timeout=5)
            log.info("Mock server 已停止")

    def set_mock_response(self, path, response):
        """
        设置模拟的响应数据

        :param path: 请求路径
        :param response: 响应数据，可以是字典、MockResponse对象
        :return: None
        """
        MockHandler.set_mock_response(path, response)

    def set_mock_callback(self, path, callback):
        """
        设置动态回调函数

        :param path: 请求路径
        :param callback: 回调函数，签名: callback(method, headers, body, query_params)
        :return: None

        示例:
        >>> def dynamic_handler(method, headers, body, query_params):
        ...     if method == 'POST' and body.get('action') == 'create':
        ...         return {'status': 'created', 'id': 123}
        ...     return {'status': 'ok'}
        >>> mock_server.set_mock_callback('/api/resource', dynamic_handler)
        """
        MockHandler.set_mock_callback(path, callback)

    def clear_mock_responses(self):
        MockHandler.clear_mock_responses()
    
    def get_base_url(self):
        """
        获取Mock服务器的基础URL
        
        :return: 基础URL字符串，例如 'http://localhost:8899'
        """
        return f"http://{self.host}:{self.port}"


class UnitTestMock:
    """
    基于unittest.mock的轻量级Mock，适用于单元测试
    提供对象级别的Mock功能，用于隔离依赖、验证调用关系等
    create_mock(): 创建命名或未命名的 Mock 对象
    get_mock() / remove_mock(): 管理 Mock 对象的生命周期
    patch_object(): 动态替换对象的属性或方法
    unpatch_object(): 恢复被替换的属性或方法
    verify_call(): 验证 Mock 的调用情况
    get_call_history(): 获取详细的调用历史
    """

    def __init__(self):
        self.mocks = {}
        self._lock = threading.Lock()

    def create_mock(self, name=None, spec=None, **kwargs):
        """
        创建一个新的Mock对象

        :param name: Mock的名称，用于标识
        :param spec: 规格，可以是类或实例，Mock将遵循其接口
        :param kwargs: 其他Mock配置参数
        :return: Mock对象
        """
        mock_obj = MagicMock(spec=spec, **kwargs)
        if name:
            with self._lock:
                self.mocks[name] = mock_obj
        return mock_obj

    def get_mock(self, name):
        """
        获取已创建的Mock对象

        :param name: Mock的名称
        :return: Mock对象，不存在则返回None
        """
        with self._lock:
            return self.mocks.get(name)

    def remove_mock(self, name):
        """
        移除指定的Mock对象

        :param name: Mock的名称
        :return: None
        """
        with self._lock:
            if name in self.mocks:
                del self.mocks[name]
                log.debug(f"已删除模拟'{name}'")

    def clear_all_mocks(self):
        """
        清空所有Mock对象
        :return: None
        """
        with self._lock:
            self.mocks.clear()
            log.debug("所有模拟均已清除")

    def patch_object(self, obj, attr, **kwargs):
        """
        模拟对象的属性或方法

        :param obj: 目标对象
        :param attr: 属性或方法名
        :param kwargs: Mock配置参数
        :return: Mock对象
        """
        original = getattr(obj, attr, None)
        mock_obj = MagicMock(**kwargs)
        setattr(obj, attr, mock_obj)

        mock_obj._original_value = original
        mock_obj._patched_object = obj
        mock_obj._patched_attr = attr

        log.debug(f"Patched {obj.__class__.__name__}.{attr} with mock")
        return mock_obj

    def unpatch_object(self, mock_obj):
        """
        恢复被模拟的对象属性

        :param mock_obj: 之前通过patch_object创建的Mock对象
        :return: None
        """
        if hasattr(mock_obj, '_patched_object'):
            obj = mock_obj._patched_object
            attr = mock_obj._patched_attr
            original = getattr(mock_obj, '_original_value', None)

            if original is not None:
                setattr(obj, attr, original)
            else:
                delattr(obj, attr)

            log.debug(f"Unpatched {obj.__class__.__name__}.{attr}")

    def verify_call(self, mock_obj, expected_calls=None, call_count=None):
        """
        验证Mock对象的调用情况

        :param mock_obj: Mock对象
        :param expected_calls: 期望的调用列表
        :param call_count: 期望的调用次数
        :return: bool，验证是否通过
        """
        try:
            if call_count is not None:
                assert mock_obj.call_count == call_count, \
                    f"Expected {call_count} calls, got {mock_obj.call_count}"

            if expected_calls:
                mock_obj.assert_has_calls(expected_calls)

            log.debug(f"Mock调用验证成功")
            return True
        except AssertionError as e:
            log.error(f"Mock调用验证失败: {e}")
            return False

    def get_call_history(self, mock_obj):
        """
        获取Mock对象的调用历史

        :param mock_obj: Mock对象
        :return: 调用历史列表
        """
        return {
            'call_count': mock_obj.call_count,
            'calls': [str(call) for call in mock_obj.call_args_list],
            'method_calls': [str(call) for call in mock_obj.method_calls]
        }


mock_server = MockServer()
mock_helper = UnitTestMock()

"""
使用示例 
from common.mock import mock_server
import httpx

# 启动 Mock 服务器
mock_server.start()

# 设置模拟响应
mock_server.set_mock_response('/api/users', {
    'status_code': 200,
    'body': {'users': [{'id': 1, 'name': 'Alice'}]}
})

# 发起请求测试
response = httpx.get('http://localhost:8888/api/users')
print(response.json())  # {'users': [{'id': 1, 'name': 'Alice'}]}

# 停止 Mock 服务器
mock_server.stop()
"""
