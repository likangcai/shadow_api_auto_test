# -*- coding: utf-8 -*-
# -----------------------------
# @Author    : 影子
# @Time      : 2025/3/12 09:32
# @Software  : PyCharm
# @FileName  : email.py
# -----------------------------
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config.config import config
from common.log import log

class EmailPush:
    def __init__(self):
        self.smtp_server = config.get('email.smtp_server')
        self.smtp_port = config.get('email.smtp_port', 465)
        self.sender = config.get('email.sender')
        self.password = config.get('email.password')
        self.recipients = config.get('email.recipients', [])
    
    def send(self, subject, content):
        if not self.smtp_server or not self.sender or not self.password:
            log.warning("电子邮件配置未完成")
            return False
        
        try:
            msg = MIMEMultipart()
            msg['From'] = self.sender
            msg['To'] = ', '.join(self.recipients)
            msg['Subject'] = subject
            
            msg.attach(MIMEText(content, 'html', 'utf-8'))
            
            # 根据端口选择连接方式
            if self.smtp_port == 465:
                # SSL 连接
                with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port) as server:
                    server.login(self.sender, self.password)
                    server.send_message(msg)
            else:
                # STARTTLS 连接（端口 587 或其他）
                with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                    server.ehlo()
                    server.starttls()
                    server.ehlo()
                    server.login(self.sender, self.password)
                    server.send_message(msg)
            
            log.info("邮件发送成功")
            return True
        except Exception as e:
            log.error(f"邮件发送失败: {str(e)}")
            return False

email_push = EmailPush()
