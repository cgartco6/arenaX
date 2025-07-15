import stripe
import os
import json
import time
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Stripe
stripe.api_key = os.getenv('STRIPE_KEY')
stripe_account = os.getenv('STRIPE_ACCOUNT_ID')

class StripeManager:
    def __init__(self):
        self.webhook_secret = os.getenv('STRIPE_WEBHOOK_SECRET')
        self.default_currency = 'usd'
    
    def create_customer(self, user_id, email, name):
        """Create a new Stripe customer"""
        try:
            customer = stripe.Customer.create(
                email=email,
                name=name,
                metadata={'user_id': user_id},
                stripe_account=stripe_account
            )
            return customer
        except stripe.error.StripeError as e:
            self.log_error('create_customer', str(e))
            return None
    
    def create_payment_intent(self, amount, currency, customer_id=None, metadata=None):
        """Create a payment intent for one-time purchases"""
        try:
            intent = stripe.PaymentIntent.create(
                amount=int(amount * 100),
                currency=currency.lower(),
                customer=customer_id,
                metadata=metadata or {},
                automatic_payment_methods={"enabled": True},
                stripe_account=stripe_account
            )
            return intent
        except stripe.error.StripeError as e:
            self.log_error('create_payment_intent', str(e))
            return None
    
    def create_setup_intent(self, customer_id):
        """Create setup intent for saving payment methods"""
        try:
            intent = stripe.SetupIntent.create(
                customer=customer_id,
                payment_method_types=["card"],
                usage="off_session",
                stripe_account=stripe_account
            )
            return intent
        except stripe.error.StripeError as e:
            self.log_error('create_setup_intent', str(e))
            return None
    
    def handle_webhook(self, payload, sig_header):
        """Process Stripe webhook events"""
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, self.webhook_secret
            )
            
            # Handle specific events
            event_type = event['type']
            if event_type == 'payment_intent.succeeded':
                self.handle_payment_success(event)
            elif event_type == 'invoice.payment_succeeded':
                self.handle_subscription_payment(event)
            elif event_type == 'customer.subscription.deleted':
                self.handle_subscription_canceled(event)
            elif event_type == 'charge.refunded':
                self.handle_refund(event)
            
            return True
        except stripe.error.SignatureVerificationError as e:
            self.log_error('webhook_signature', str(e))
            return False
        except Exception as e:
            self.log_error('webhook_processing', str(e))
            return False
    
    def handle_payment_success(self, event):
        """Process successful payment"""
        payment_intent = event['data']['object']
        user_id = payment_intent['metadata'].get('user_id')
        amount = payment_intent['amount'] / 100
        currency = payment_intent['currency']
        
        # Update user's balance in database
        self.update_user_balance(user_id, amount, currency)
        
        # Log transaction
        self.log_transaction(
            payment_intent['id'],
            'payment',
            amount,
            currency,
            user_id
        )
    
    def handle_subscription_payment(self, event):
        """Process subscription payment"""
        invoice = event['data']['object']
        subscription_id = invoice['subscription']
        customer_id = invoice['customer']
        amount = invoice['amount_paid'] / 100
        currency = invoice['currency']
        
        # Get subscription details
        subscription = stripe.Subscription.retrieve(
            subscription_id,
            stripe_account=stripe_account
        )
        
        user_id = subscription['metadata'].get('user_id')
        
        # Update user's subscription status
        self.update_subscription_status(
            user_id,
            subscription_id,
            'active',
            subscription['current_period_end']
        )
        
        # Log transaction
        self.log_transaction(
            invoice['payment_intent'],
            'subscription',
            amount,
            currency,
            user_id
        )
    
    def handle_subscription_canceled(self, event):
        """Process subscription cancellation"""
        subscription = event['data']['object']
        user_id = subscription['metadata'].get('user_id')
        
        # Update user's subscription status
        self.update_subscription_status(
            user_id,
            subscription['id'],
            'canceled'
        )
    
    def handle_refund(self, event):
        """Process refunds"""
        charge = event['data']['object']
        payment_intent = charge['payment_intent']
        amount = charge['amount_refunded'] / 100
        currency = charge['currency']
        
        # Update user's balance
        self.update_user_balance(
            charge['metadata'].get('user_id'),
            -amount,
            currency
        )
    
    def update_user_balance(self, user_id, amount, currency):
        """Update user balance in database (stub implementation)"""
        print(f"Updating balance for user {user_id}: {amount} {currency}")
        # Implement actual database update
    
    def update_subscription_status(self, user_id, subscription_id, status, end_date=None):
        """Update subscription status in database (stub implementation)"""
        print(f"Updating subscription {subscription_id} to {status} for user {user_id}")
        # Implement actual database update
    
    def log_transaction(self, transaction_id, transaction_type, amount, currency, user_id):
        """Log transaction to database"""
        timestamp = datetime.utcnow().isoformat()
        data = {
            'transaction_id': transaction_id,
            'type': transaction_type,
            'amount': amount,
            'currency': currency,
            'user_id': user_id,
            'timestamp': timestamp
        }
        with open("stripe_transactions.log", "a") as f:
            f.write(json.dumps(data) + "\n")
    
    def log_error(self, context, message):
        """Log Stripe errors"""
        timestamp = datetime.utcnow().isoformat()
        error_data = {
            'context': context,
            'message': message,
            'timestamp': timestamp
        }
        with open("stripe_errors.log", "a") as f:
            f.write(json.dumps(error_data) + "\n")
    
    def list_payment_methods(self, customer_id):
        """List customer's payment methods"""
        try:
            methods = stripe.PaymentMethod.list(
                customer=customer_id,
                type="card",
                stripe_account=stripe_account
            )
            return methods
        except stripe.error.StripeError as e:
            self.log_error('list_payment_methods', str(e))
            return []
    
    def create_refund(self, payment_intent_id, amount=None):
        """Create a refund for a payment"""
        try:
            refund_params = {
                'payment_intent': payment_intent_id,
                'stripe_account': stripe_account
            }
            if amount:
                refund_params['amount'] = int(amount * 100)
                
            refund = stripe.Refund.create(**refund_params)
            return refund
        except stripe.error.StripeError as e:
            self.log_error('create_refund', str(e))
            return None

# Singleton instance for easy access
stripe_manager = StripeManager()
