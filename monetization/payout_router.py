import os
import requests
import stripe
import time
import json
from decimal import Decimal
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Stripe
stripe.api_key = os.getenv('STRIPE_KEY')
stripe_account = os.getenv('STRIPE_ACCOUNT_ID')

# Payment endpoints
VALR_API = "https://api.valr.com/v1"
TRUST_API = "https://api.trustwallet.com/payments"
FNB_SWIFT = "FIRNZAJJ"  # FNB South Africa SWIFT code

# Global cache for external accounts
external_accounts = {}

def route_payout(total_amount, currency='USD'):
    """Distribute revenue to multiple payment channels"""
    distribution = {
        'valr': Decimal('0.40'),
        'trust_wallet': Decimal('0.20'),
        'paypal': Decimal('0.20'),
        'fnb_bank': Decimal('0.20')
    }
    
    # Process each payout
    for channel, percentage in distribution.items():
        amount = total_amount * percentage
        if amount > 0.01:  # Minimum payout threshold
            try:
                if channel == 'valr':
                    valr_payout(amount, currency)
                elif channel == 'trust_wallet':
                    trust_payout(amount, currency)
                elif channel == 'paypal':
                    paypal_payout(amount, currency)
                elif channel == 'fnb_bank':
                    fnb_payout(amount, currency)
                time.sleep(2)  # Rate limiting
            except Exception as e:
                log_error(channel, str(e))

def valr_payout(amount, currency):
    """Send to VALR crypto exchange (South Africa)"""
    payload = {
        "type": "INSTANT",
        "currency": currency,
        "amount": str(amount),
        "address": os.getenv('VALR_WALLET')
    }
    response = requests.post(
        f"{VALR_API}/wallet/crypto/withdraw",
        json=payload,
        auth=(os.getenv('VALR_KEY'), os.getenv('VALR_SECRET')),
        timeout=30
    )
    if response.status_code != 200:
        raise Exception(f"VALR Error: {response.text}")
    log_transaction('VALR', amount, currency, response.status_code)

def trust_payout(amount, currency):
    """Send to Trust Wallet (Crypto)"""
    response = requests.post(
        TRUST_API,
        json={
            "asset": currency,
            "amount": str(amount),
            "destination": os.getenv('TRUST_WALLET'),
            "memo": "ArenaX Revenue"
        },
        headers={"Authorization": f"Bearer {os.getenv('TRUST_KEY')}"},
        timeout=30
    )
    if response.status_code != 200:
        raise Exception(f"Trust Wallet Error: {response.text}")
    log_transaction('Trust Wallet', amount, currency, response.status_code)

def paypal_payout(amount, currency):
    """Send to PayPal"""
    transfer = stripe.Transfer.create(
        amount=int(amount * 100),
        currency=currency.lower(),
        destination=os.getenv('PAYPAL_ID'),
        description="ArenaX Revenue",
        stripe_account=stripe_account
    )
    log_transaction('PayPal', amount, currency, transfer.status)

def fnb_payout(amount, currency='USD'):
    """Send to FNB Global Account (USD) via SWIFT"""
    # Create or retrieve external account
    account_key = f"fnb_{currency}"
    if account_key not in external_accounts:
        external_account = stripe.Account.create_external_account(
            stripe_account,
            external_account={
                "object": "bank_account",
                "country": "ZA",
                "currency": currency,
                "routing_number": FNB_SWIFT,
                "account_number": os.getenv('FNB_ACCOUNT_NUMBER'),
                "account_holder_name": os.getenv('FNB_ACCOUNT_NAME'),
                "account_holder_type": "company"
            }
        )
        external_accounts[account_key] = external_account.id
    
    # Create payout
    payout = stripe.Payout.create(
        amount=int(amount * 100),
        currency=currency,
        destination=external_accounts[account_key],
        description="ArenaX Revenue",
        metadata={"bank": "FNB Global Account"},
        stripe_account=stripe_account
    )
    
    # Verify compliance
    if not verify_fnb_transfer(payout):
        raise Exception("FNB compliance check failed")
    
    log_transaction('FNB Global', amount, currency, payout.status)

def verify_fnb_transfer(payout):
    """Compliance checks for FNB transfers"""
    # Ensure USD currency
    if payout.currency.lower() != 'usd':
        return False
    
    # Verify amount range ($50-$10,000)
    amount = payout.amount / 100
    if not (50 <= amount <= 10000):
        return False
    
    # Check destination metadata
    if payout.metadata.get('bank') != "FNB Global Account":
        return False
    
    return True

def log_transaction(platform, amount, currency, status):
    print(f"[SUCCESS] Sent {amount:.2f} {currency} to {platform}. Status: {status}")
    # Add to audit log
    with open("payout_audit.log", "a") as f:
        f.write(f"{time.ctime()},{platform},{amount:.2f},{currency},{status}\n")

def log_error(channel, message):
    print(f"[ERROR] {channel} payout failed: {message}")
    with open("payout_errors.log", "a") as f:
        f.write(f"{time.ctime()},{channel},{message}\n")

if __name__ == "__main__":
    # Get total revenue from database
    total_revenue = get_daily_revenue()  # Implement this function
    route_payout(total_revenue, 'USD')
