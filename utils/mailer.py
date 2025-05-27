import smtplib
from email.message import EmailMessage
import os

# Enhanced mailer to support attachments and named parameters

def send_email(smtp_user, smtp_pass, from_addr, to_addrs, subject, body, attachments=None):
    """
    Send an email with optional attachments via SMTP.

    Parameters:
    - smtp_user: SMTP username
    - smtp_pass: SMTP password
    - from_addr: sender email address
    - to_addrs: single email or list of recipient emails
    - subject: email subject
    - body: plain-text email body
    - attachments: list of filepaths to attach (PDFs assumed)
    """
    if attachments is None:
        attachments = []

    msg = EmailMessage()
    msg["From"] = from_addr
    if isinstance(to_addrs, (list, tuple)):
        msg["To"] = ", ".join(to_addrs)
    else:
        msg["To"] = to_addrs
    msg["Subject"] = subject
    msg.set_content(body)

    # Attach files
    for file in attachments:
        try:
            with open(file, "rb") as f:
                data = f.read()
                maintype, subtype = "application", "pdf"
                msg.add_attachment(data, maintype=maintype, subtype=subtype, filename=os.path.basename(file))
        except Exception as e:
            print(f"Warning: could not attach {file}: {e}")

    # Send via Zoho SMTP
    with smtplib.SMTP("smtp.zoho.com", 587) as s:
        s.starttls()
        s.login(smtp_user, smtp_pass)
        s.send_message(msg)
