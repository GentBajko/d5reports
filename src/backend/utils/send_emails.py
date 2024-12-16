import smtplib
from email.mime.text import MIMEText

from config.env import ENV


def send_email_to_user(to: str, title: str, message: str):
    msg = MIMEText(message, "html")
    msg["Subject"] = title
    msg["From"] = ENV.EMAIL
    msg["To"] = to

    with smtplib.SMTP_SSL(ENV.EMAIL_HOST, 465) as server:
        server.login(ENV.EMAIL, ENV.EMAIL_PASSWORD)
        server.send_message(msg)
