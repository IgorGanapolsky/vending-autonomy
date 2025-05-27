#!/usr/bin/env python3
"""
Generate a PDF revenue-share vending agreement and email it automatically via Zoho SMTP.
"""
import os
import sys
from datetime import datetime
from fpdf import FPDF
import utils.mailer as mailer

# Config: read from environment
SMTP_USER = os.getenv("ZOHO_SMTP_USER")
SMTP_PASS = os.getenv("ZOHO_SMTP_PASS")
FROM_EMAIL = SMTP_USER
TO_EMAIL = os.getenv("CONTRACT_RECIPIENT", SMTP_USER)  # default to self if not set

DEFAULT_COMMISSION = "30%"

PDF_TEMPLATE = (
    "REVENUE-SHARE VENDING AGREEMENT\n\n"
    "Date: {date}\n"
    "Operator: Igor Ganapolsky\n"
    "Supplier: {supplier_name}\n"
    "\n"
    "1. Placement & Maintenance\n"
    "   Operator will place and service vending machines at locations provided by Supplier.\n"
    "2. Revenue Share\n"
    "   Operator receives {commission} of net sales from machines placed.\n"
    "3. Term & Termination\n"
    "   Agreement starts on date above and may be ended by either party with 30 days notice.\n"
)


def generate_pdf(supplier_name: str, commission: str) -> str:
    """
    Generate a PDF agreement and return the filepath.
    """
    date_str = datetime.utcnow().strftime("%Y-%m-%d")
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    text = PDF_TEMPLATE.format(
        date=date_str,
        supplier_name=supplier_name,
        commission=commission
    )
    for line in text.split("\n"):
        pdf.multi_cell(0, 8, line)
    filename = f"agreement_{supplier_name.replace(' ', '_')}_{date_str}.pdf"
    pdf.output(filename)
    return filename


def send_contract(supplier_name: str, supplier_email: str, commission: str = DEFAULT_COMMISSION):
    """
    Generate PDF contract and email it via SMTP.
    """
    # 1) Generate PDF
    pdf_file = generate_pdf(supplier_name, commission)

    # 2) Email it
    subject = f"Revenue-Share Agreement for {supplier_name}"
    body = (
        f"Hello {supplier_name},\n\n"
        "Please find attached our revenue-share vending agreement. "
        "Sign and return at your convenience!\n\n"
        "Regards,\nIgor Ganapolsky"
    )
    mailer.send_email(
        smtp_user=SMTP_USER,
        smtp_pass=SMTP_PASS,
        from_addr=FROM_EMAIL,
        to_addrs=[supplier_email],
        subject=subject,
        body=body,
        attachments=[pdf_file]
    )
    print(f"Contract emailed to {supplier_email}: {pdf_file}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: contract_manager.py <Supplier Name> <Supplier Email> [commission]")
        sys.exit(1)
    name = sys.argv[1]
    email = sys.argv[2]
    comm = sys.argv[3] if len(sys.argv) >= 4 else DEFAULT_COMMISSION
    send_contract(name, email, comm)
