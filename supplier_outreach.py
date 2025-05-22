#!/usr/bin/env python3
"""
Find local Broward‐County vending machine providers
offering “free placement” and send them your 30% revenue‐share pitch.
"""

import requests
from bs4 import BeautifulSoup
import csv
import os
from utils.mailer import send_email

# ----- CONFIG -----
COMMISSION_SPLIT = "30%"
PRODUCT_FOCUS = "snacks only"
SMTP_USER = os.getenv("ZOHO_SMTP_USER")
SMTP_PASS = os.getenv("ZOHO_SMTP_PASS")

# A. Scrape a shortlist of known distributor URLs
DISTRIBUTOR_SITES = [
    "https://www.ustechvending.com/free-placement",
    "https://www.vendtechusa.com/programs",
    # …add more or extend via Google Places API in the future
]

def fetch_offers(url):
    """Return list of (company, contact_email, details_url)."""
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    offers = []
    for link in soup.select("a[href*='mailto:']"):
        email = link["href"].split("mailto:")[1]
        company = soup.select_one("h1, h2").get_text(strip=True)
        offers.append((company, email, url))
    return offers

def gather_offers():
    all_offers = []
    for site in DISTRIBUTOR_SITES:
        try:
            offers = fetch_offers(site)
            all_offers.extend(offers)
        except Exception as e:
            print(f"Error scraping {site}: {e}")
    return all_offers

def draft_pitch(company, email, url):
    subject = f"Free‐placement vending in Broward County – 30% revenue‐share"
    body = f"""
Hi {company} team,

I’m Igor Ganapolsky, a Broward‐based operator interested in your free‐placement vending program.
I’ll handle location scouting, machine servicing oversight, and daily cash reconciliation.
In exchange, I’d like to keep {COMMISSION_SPLIT} of net sales on **{PRODUCT_FOCUS}** machines.

Could we discuss next steps? You can reach me anytime at {SMTP_USER} or reply to this email.

Best,
Igor
"""
    return subject, body

def main():
    offers = gather_offers()
    with open("leads.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Company", "Email", "Source URL"])
        for comp, email, url in offers:
            writer.writerow([comp, email, url])
            subj, body = draft_pitch(comp, email, url)
            send_email(smtp_user=SMTP_USER,
                       smtp_pass=SMTP_PASS,
                       to_addr=email,
                       subject=subj,
                       body=body)
    print(f"Contacted {len(offers)} suppliers. Leads saved to leads.csv.")

if __name__ == "__main__":
    main()
