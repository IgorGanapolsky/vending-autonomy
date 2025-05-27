#!/usr/bin/env python3
"""
Generate and send revenue-share vending contracts via DocuSign.
"""

import os
import sys
import base64
from docusign_esign import ApiClient, EnvelopesApi
from docusign_esign.models import (
    EnvelopeDefinition, Document, Signer, SignHere, Tabs, Recipients
)

# ----- CONFIGURATION (set these as GitHub Secrets or env vars) -----
# Your DocuSign integration key (Client ID)
DS_INTEGRATOR_KEY = os.getenv("DS_INTEGRATOR_KEY")
# The user ID to impersonate (GUID)
DS_IMPERSONATED_USER_ID = os.getenv("DS_IMPERSONATED_USER_ID")
# OAuth base path (e.g., account-d.docusign.com)
DS_OAUTH_SERVER = os.getenv("DS_OAUTH_SERVER", "account-d.docusign.com")
# Your RSA private key, PEM format, with newline escapes
DS_PRIVATE_KEY = os.getenv("DS_PRIVATE_KEY")
# Your DocuSign account ID
DS_ACCOUNT_ID = os.getenv("DS_ACCOUNT_ID")

# Revenue-share terms
default_commission = "30%"


def authenticate() -> ApiClient:
    """
    Authenticate via JWT and return a configured ApiClient.
    """
    api_client = ApiClient()
    api_client.set_oauth_host_name(DS_OAUTH_SERVER)
    token_response = api_client.request_jwt_user_token(
        client_id=DS_INTEGRATOR_KEY,
        user_id=DS_IMPERSONATED_USER_ID,
        oauth_host_name=DS_OAUTH_SERVER,
        private_key_bytes=DS_PRIVATE_KEY.encode("utf-8"),
        expires_in=3600
    )
    access_token = token_response.access_token
    api_client.host = f"https://{DS_OAUTH_SERVER}/restapi"
    api_client.set_default_header("Authorization", f"Bearer {access_token}")
    return api_client


def send_contract(supplier_name: str, supplier_email: str, commission: str = default_commission):
    """
    Generate a simple txt contract and send it via DocuSign.
    """
    # 1) Create the contract text
    contract_text = f"""
REVENUE-SHARE VENDING AGREEMENT

This Agreement is made between Igor Ganapolsky (Operator) and {supplier_name} (Supplier).

1. Placement & Maintenance
Operator will place and supervise vending machines at locations provided by Supplier.

2. Revenue Share
Operator shall receive {commission} of net sales from all machines placed under this Agreement.

3. Term & Termination
This Agreement commences on the date of last signature and continues until terminated by either party with 30 days' notice.

Operator Signature: ______________________   Date: _______________
Supplier Signature: _____________________   Date: _______________
"""
    # 2) Write to a .txt file
    filename = "contract.txt"
    with open(filename, "w") as f:
        f.write(contract_text)

    # 3) Base64-encode the file
    with open(filename, "rb") as f:
        doc_b64 = base64.b64encode(f.read()).decode("ascii")

    # 4) Build the envelope definition
    envelope_def = EnvelopeDefinition(
        email_subject="Please sign the revenue-share vending agreement",
        documents=[
            Document(
                document_base64=doc_b64,
                name="Revenue-Share Agreement.txt",
                file_extension="txt",
                document_id="1"
            )
        ],
        recipients=Recipients(
            signers=[
                Signer(
                    email=supplier_email,
                    name=supplier_name,
                    recipient_id="1",
                    routing_order="1",
                    tabs=Tabs(
                        sign_here_tabs=[
                            SignHere(
                                document_id="1",
                                page_number="1",
                                recipient_id="1",
                                tab_label="SignHere",
                                x_position="200",
                                y_position="600"
                            )
                        ]
                    )
                )
            ]
        ),
        status="sent"
    )

    # 5) Authenticate and send
    api_client = authenticate()
    envelopes_api = EnvelopesApi(api_client)
    summary = envelopes_api.create_envelope(
        account_id=DS_ACCOUNT_ID,
        envelope_definition=envelope_def
    )
    print(f"Envelope sent to {supplier_email}. Envelope ID: {summary.envelope_id}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: contract_manager.py <Supplier Name> <Supplier Email>")
        sys.exit(1)
    send_contract(sys.argv[1], sys.argv[2])
