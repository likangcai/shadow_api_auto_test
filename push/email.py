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
            log.warning("Email configuration is not complete")
            return False
        
        try:
            msg = MIMEMultipart()
            msg['From'] = self.sender
            msg['To'] = ', '.join(self.recipients)
            msg['Subject'] = subject
            
            msg.attach(MIMEText(content, 'html', 'utf-8'))
            
            with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port) as server:
                server.login(self.sender, self.password)
                server.send_message(msg)
            log.info("Email sent successfully")
            return True
        except Exception as e:
            log.error(f"Failed to send email: {str(e)}")
            return False

email_push = EmailPush()
