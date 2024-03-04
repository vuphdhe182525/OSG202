import email  
import smtplib
import re
import getpass
import imaplib
from email.message import EmailMessage
from concurrent.futures import ThreadPoolExecutor
import time

# Hàm nhập tên người dùng và mật khẩu từ bàn phím
def get_email_credentials():
    imap_username = input("Nhập tên người dùng (email): ")
    imap_password = input("Nhập mật khẩu (email): ")
    return imap_username, imap_password

# Hàm đọc tệp cấu hình và trả về một từ điển các mẫu và thông điệp phản hồi
def read_config(filename):
    patterns = {}
    with open(filename, 'r') as file:
        for line in file:
            key, value = line.strip().split(':')
            patterns[key.strip()] = value.strip()
    return patterns

# Hàm kiểm tra xem email có khớp với mẫu nào trong từ điển không
def match_pattern(email_subject, patterns):
    # Chuyển đổi tiêu đề email và mẫu về chữ thường
    email_subject_lower = email_subject.lower()

    for pattern, response in patterns.items():
        if re.search(pattern, email_subject, re.IGNORECASE):
            return response
    return None
