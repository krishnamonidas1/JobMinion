import smtplib, os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv
load_dotenv()

email    = os.environ.get('GMAIL_ADDRESS')
password = os.environ.get('GMAIL_APP_PASSWORD')
fallback = os.environ.get('FALLBACK_EMAIL')

print(f'GMAIL_ADDRESS  : {email}')
print(f'FALLBACK_EMAIL : {fallback}')
print(f'Password len   : {len(password) if password else 0}')

recipient = "krishnamonidas44@outlook.com"  # use any email you have access to
print(f'Sending to     : {recipient}')

msg = MIMEMultipart()
msg['Subject'] = 'Pipeline Test - AI Job Agent'
msg['From']    = email
msg['To']      = recipient
msg.attach(MIMEText('Test from email_sender pipeline.', 'plain'))

try:
    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.ehlo()
        server.starttls()
        server.login(email, password)
        result = server.sendmail(email, recipient, msg.as_string())
        print(f'Sent! SMTP result: {result}')
except Exception as e:
    print(f'Failed: {e}')