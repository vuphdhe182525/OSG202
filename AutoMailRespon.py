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

# Hàm gửi phản hồi tự động
def send_auto_response(sender_email, response):
    # Thiết lập thông tin tài khoản email của bạn
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587  # Gmail sử dụng cổng 587
    smtp_username = imap_username
    smtp_password = imap_password
    smtp_from = smtp_username
    smtp_to = sender_email

# Soạn email phản hồi tự động
    subject = 'Phản hồi tự động'
    body = response

# Tạo đối tượng EmailMessage
    msg = EmailMessage()
    msg['From'] = smtp_from
    msg['To'] = smtp_to
    msg['Subject'] = subject
    msg.set_content(body)

 # Gửi email
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(smtp_username, smtp_password)
        server.send_message(msg)

def count_total_emails(imap_server, username, password):
    mail = imaplib.IMAP4_SSL(imap_server)
    mail.login(username, password)
    mail.select('inbox')
    result, data = mail.search(None, 'ALL')
    if result == 'OK':
        return len(data[0].split())
    else:
        return 0
        
# Thiết lập thông tin tài khoản email của bạn
imap_server = 'imap.gmail.com'
imap_username, imap_password = get_email_credentials()

# Đọc tệp cấu hình
config_file = '/home/config.txt'
patterns = read_config(config_file)

# Đếm tổng số email trong hộp thư đến ban đầu
total_emails_initial = count_total_emails(imap_server, imap_username, imap_password)

# Chờ 30 giây trước khi bắt đầu vòng lặp
time.sleep(30)

# Khởi tạo danh sách lưu trữ thông tin về các email mới (ở mức độ toàn cục)
new_emails_info = []
print("Các email mới đến:")

while True:
# Đếm tổng số email trong hộp thư đến hiện tại
total_emails_current = count_total_emails(imap_server, imap_username, imap_password)

# Nếu số email trong hộp thư không thay đổi
    if total_emails_current == total_emails_initial:
        # Chờ thêm 60 giây
        time.sleep(60)
        continue

# Nếu số email trong hộp thư thay đổi
    else:
        mail = imaplib.IMAP4_SSL(imap_server)
        mail.login(imap_username, imap_password)
        mail.select('inbox')
        
        # Tìm kiếm email mới
        result, data = mail.search(None, 'ALL')
        
        if result == 'OK':
            email_ids = data[0].split()
            new_emails = email_ids[-(total_emails_current - total_emails_initial):]
            for email_id in email_ids[-(total_emails_current - total_emails_initial):]:
                result, email_data = mail.fetch(email_id, '(RFC822)')
                raw_email = email_data[0][1]
                msg = email.message_from_bytes(raw_email)
                sender_email = msg['From']
                email_subject = msg['Subject']

# Kiểm tra xem email có khớp với mẫu nào trong từ điển không
                response = match_pattern(email_subject, patterns)
                if response:
                    # Gửi phản hồi tự động
                    send_auto_response(sender_email, response)
                    
                # Lưu thông tin về email mới vào danh sách
                new_emails_info.append({'Sender': sender_email, 'Subject': email_subject})

                # Hàm tạo file từ tiêu đề email "Create - File1"
                def create_file_from_email(email_subject, email_content):
                    if "Create - " in email_subject:
                       file_name = email_subject.split("Create - ")[1].strip() + ".txt"
                       with open(file_name, "w") as file:
                           file.write(email_content)
                # Hàm đọc nội dung của file
                def read_file_content(file_name):
                    if os.path.exists(file_name):
                        with open(file_name, "r") as file:
                            return file.read()
                    return None

                # Xử lý email mới
                if new_emails_info:
                    for email_info in new_emails_info:
                        sender_email = email_info['Sender']
                        email_subject = email_info['Subject']
                        print(f" {sender_email},-{email_subject}")

                        # Trích xuất nội dung email từ dữ liệu thu thập được từ server email
                        result, email_data = mail.fetch(email_id, '(RFC822)')
                        raw_email = email_data[0][1]
                        msg = email.message_from_bytes(raw_email)
                        # Kiểm tra nếu email chỉ có một phần văn bản
                        if msg.is_multipart():
                            for part in msg.get_payload():
                                if part.get_content_type() == 'text/plain':
                                   email_content = part.get_payload(decode=True).decode()
                                   break
                        else:
                           email_content = msg.get_payload(decode=True).decode()

                        # Kiểm tra nếu có email với tiêu đề "Create - File1"
                        if "Create - " in email_subject:
                            create_file_from_email(email_subject, email_content)
        
                        # Kiểm tra nếu có email với tiêu đề "Read - File1"
                        if "Read - " in email_subject:
                            file_name = email_subject.split("Read - ")[1].strip() + ".txt"
                            response_content = read_file_content(file_name)
                            if response_content:

                                # Gửi phản hồi với nội dung của file
send_auto_response(sender_email, response_content)
                            else:
                                send_auto_response(sender_email, f"Không tìm thấy file {file_name}")

        # Cập nhật lại tổng số email ban đầu
        total_emails_initial = total_emails_current
        # Đóng kết nối
        mail.close()
        mail.logout()

 # In thông tin về các email mới đến
        if new_emails_info:
            for email_info in new_emails_info:
                print(f" {email_info['Sender']},-{email_info['Subject']}")
            new_emails_info = []  # Đặt lại danh sách để lưu trữ thông tin về email mới

        # Chờ 60 giây trước khi quét email tiếp theo
        time.sleep(60)
