from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import threading
import time
from common.log import log

class MockHandler(BaseHTTPRequestHandler):
    mock_responses = {}
    
    @classmethod
    def set_mock_response(cls, path, response):
        cls.mock_responses[path] = response
    
    @classmethod
    def clear_mock_responses(cls):
        cls.mock_responses.clear()
    
    def do_GET(self):
        if self.path in self.mock_responses:
            response = self.mock_responses[self.path]
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_POST(self):
        if self.path in self.mock_responses:
            response = self.mock_responses[self.path]
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

class MockServer:
    def __init__(self, host='localhost', port=8888):
        self.host = host
        self.port = port
        self.server = None
        self.thread = None
    
    def start(self):
        self.server = HTTPServer((self.host, self.port), MockHandler)
        self.thread = threading.Thread(target=self.server.serve_forever)
        self.thread.daemon = True
        self.thread.start()
        log.info(f"Mock server started at http://{self.host}:{self.port}")
    
    def stop(self):
        if self.server:
            self.server.shutdown()
            self.server.server_close()
            log.info("Mock server stopped")
    
    def set_mock_response(self, path, response):
        MockHandler.set_mock_response(path, response)
    
    def clear_mock_responses(self):
        MockHandler.clear_mock_responses()

mock_server = MockServer()
