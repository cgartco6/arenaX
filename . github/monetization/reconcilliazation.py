import stripe
import os
import csv
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()
stripe.api_key = os.getenv('STRIPE_KEY')
stripe_account = os.getenv('STRIPE_ACCOUNT_ID')

def reconcile_payouts():
    """Verify completed payouts"""
    # Get yesterday's date
    yesterday = datetime.now() - timedelta(days=1)
    start_date = int(yesterday.timestamp())
    
    # Retrieve Stripe payouts
    payouts = stripe.Payout.list(
        created={'gte': start_date},
        stripe_account=stripe_account,
        limit=100
    )
    
    # Process payouts
    for payout in payouts.auto_paging_iter():
        if payout.destination.startswith('ba_'):
            reconcile_bank_payout(payout)
        elif payout.destination.startswith('acct_'):
            reconcile_paypal_payout(payout)

def reconcile_bank_payout(payout):
    """Reconcile FNB bank transfers"""
    if payout.metadata.get('bank') == "FNB Global Account":
        # Verify transaction details
        if payout.status == 'paid':
            log_reconciliation(payout.id, 'FNB', 'success')
        elif payout.status == 'failed':
            log_reconciliation(payout.id, 'FNB', 'failed')
            # Trigger reprocessing
            reprocess_payout(payout)

def reconcile_paypal_payout(payout):
    """Reconcile PayPal transfers"""
    if payout.status == 'paid':
        log_reconciliation(payout.id, 'PayPal', 'success')
    elif payout.status == 'failed':
        log_reconciliation(payout.id, 'PayPal', 'failed')
        reprocess_payout(payout)

def reprocess_payout(payout):
    """Reprocess failed payout"""
    amount = payout.amount / 100
    currency = payout.currency
    if payout.metadata.get('bank') == "FNB Global Account":
        # Retry via PayPal as fallback
        stripe.Transfer.create(
            amount=int(amount * 100),
            currency=currency,
            destination=os.getenv('PAYPAL_ID'),
            description="Reprocessed FNB Payout",
            stripe_account=stripe_account
        )
    else:
        # Retry original method
        # (Implement retry logic for other methods)
        pass

def log_reconciliation(payout_id, platform, status):
    print(f"Reconciled {payout_id} ({platform}): {status}")
    with open("reconciliation_log.csv", "a") as f:
        writer = csv.writer(f)
        writer.writerow([datetime.now().isoformat(), payout_id, platform, status])

if __name__ == "__main__":
    reconcile_payouts()
