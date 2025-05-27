#!/usr/bin/env python3
"""
Automated discovery and outreach to free-placement vending suppliers in Broward County.
"""

import os
from googlesearch import search
import requests
from bs4 import BeautifulSoup
import csv
from utils.mailer import send_email

# ----- CONFIG -----
COMMISSION_SPLIT = "30%"
PRODUCT_FOCUS = "snacks only"
SMTP_USER = os.getenv("ZOHO_SMTP_USER")
SMTP_PASS = os.getenv("ZOHO_SMTP_PASS")


def discover_supplier_sites(query="free placement vending Broward County", num=10):
    """
    Return a list of vending supplier URLs via Google Search.
    """
    results = []
    for url in search(query, num_results=num):
        if "vending" in url.lower():
            results.append(url)
    return results

def fetch_offers(url):
    """
    Scrape a single page and return a list of
    (company_name, contact_email, source_url).
    """
    offers = []
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        company_el = soup.select_one("h1, h2")
        company = company_el.get_text(strip=True) if company_el else url
        for link in soup.select("a[href*='mailto:']"):
            email = link["href"].split("mailto:")[1]
            offers.append((company, email, url))
    except Exception as e:
        print(f"Error scraping {url}: {e}")
    return offers


def main():
    # 1) Discover
    sites = discover_supplier_sites()
    offers = []

    # 2) Scrape each
    for site in sites:
        offers.extend(fetch_offers(site))

    # 3) Write leads.csv
    with open("leads.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Company", "Email", "Source URL"])
        for comp, email, src in offers:
            writer.writerow([comp, email, src])

    # 4) Send outreach emails
    for comp, email, src in offers:
        subject = f"Free-placement vending in Broward County – {COMMISSION_SPLIT} revenue-share"
        body = f"""
Hi {comp} team,

I'm Igor Ganapolsky, a Broward-based operator interested in your free-placement vending program.
I'll handle location scouting, servicing oversight, and reconciliation,
and in exchange would like to keep {COMMISSION_SPLIT} of net sales on **{PRODUCT_FOCUS}** machines.

Could we discuss next steps? You can reach me at {SMTP_USER} or simply reply to this email.

Best,
Igor
"""
        send_email(
            smtp_user=SMTP_USER,
            smtp_pass=SMTP_PASS,
            to_addr=email,
            subject=subject,
            body=body
        )

    print(f"Contacted {len(offers)} suppliers. Leads saved to leads.csv.")


if __name__ == "__main__":
    main()
