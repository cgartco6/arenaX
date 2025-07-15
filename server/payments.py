import stripe
import os
from dotenv import load_dotenv

load_dotenv()
stripe.api_key = os.getenv('STRIPE_KEY')
stripe_account = os.getenv('STRIPE_ACCOUNT_ID')

async def process_payment(payment_data):
    """Handle different payment types"""
    payment_type = payment_data.get('type', 'one_time')
    currency = payment_data.get('currency', 'usd').lower()
    amount = float(payment_data['amount'])
    
    if payment_type == 'subscription':
        return await create_subscription(payment_data)
    elif payment_type == 'one_time':
        return stripe.PaymentIntent.create(
            amount=int(amount * 100),
            currency=currency,
            payment_method_types=["card"],
            stripe_account=stripe_account
        )
    elif payment_type == 'crypto':
        return handle_crypto_payment(payment_data)
    else:
        raise ValueError("Invalid payment type")

async def create_subscription(payment_data):
    """Create a subscription plan"""
    # Create product if not exists
    product = stripe.Product.create(
        name=payment_data['name'],
        type='service',
        stripe_account=stripe_account
    )
    
    # Create price
    price = stripe.Price.create(
        unit_amount=int(float(payment_data['amount']) * 100),
        currency=payment_data.get('currency', 'usd').lower(),
        recurring={"interval": "month"},
        product=product.id,
        stripe_account=stripe_account
    )
    
    # Create subscription
    return stripe.Subscription.create(
        customer=payment_data['customer_id'],
        items=[{"price": price.id}],
        stripe_account=stripe_account
    )

def handle_crypto_payment(payment_data):
    """Handle cryptocurrency payments"""
    return {
        "status": "pending",
        "crypto_address": "0xYourCryptoAddress",
        "amount": payment_data['amount'],
        "currency": payment_data.get('currency', 'usdt'),
        "instructions": "Send exact amount to this address"
    }
