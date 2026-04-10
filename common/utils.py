import random
import string
from datetime import datetime, timedelta

class Utils:
    @staticmethod
    def generate_random_string(length=10):
        letters = string.ascii_letters
        return ''.join(random.choice(letters) for i in range(length))
    
    @staticmethod
    def generate_random_number(min_value=0, max_value=1000):
        return random.randint(min_value, max_value)
    
    @staticmethod
    def generate_random_email():
        domain = random.choice(['gmail.com', 'yahoo.com', 'hotmail.com', 'example.com'])
        username = Utils.generate_random_string(8)
        return f"{username}@{domain}"
    
    @staticmethod
    def generate_random_phone():
        return f"1{random.randint(3, 9)}{''.join([str(random.randint(0, 9)) for _ in range(9)])}"
    
    @staticmethod
    def generate_random_date(start_date=None, end_date=None):
        if start_date is None:
            start_date = datetime.now() - timedelta(days=365)
        if end_date is None:
            end_date = datetime.now()
        delta = end_date - start_date
        random_days = random.randint(0, delta.days)
        return start_date + timedelta(days=random_days)
    
    @staticmethod
    def generate_random_boolean():
        return random.choice([True, False])

utils = Utils()
