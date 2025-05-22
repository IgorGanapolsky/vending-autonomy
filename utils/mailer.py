import smtplib
from email.message import EmailMessage

def send_email(smtp_user, smtp_pass, to_addr, subject, body):
    msg = EmailMessage()
    msg["From"] = smtp_user
    msg["To"] = to_addr
    msg["Subject"] = subject
    msg.set_content(body)

    with smtplib.SMTP("smtp.zoho.com", 587) as s:
        s.starttls()
        s.login(smtp_user, smtp_pass)
        s.send_message(msg)
