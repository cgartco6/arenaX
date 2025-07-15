import stripe
import os
import time
from datetime import datetime
from dotenv import load_dotenv
from .stripe_integration import stripe_manager

# Load environment variables
load_dotenv()

stripe.api_key = os.getenv('STRIPE_KEY')
stripe_account = os.getenv('STRIPE_ACCOUNT_ID')

class SubscriptionManager:
    def __init__(self):
        self.default_currency = 'usd'
        self.trial_period_days = 7
    
    def create_subscription_plan(self, name, price, interval="month", currency=None):
        """Create a new subscription plan"""
        currency = currency or self.default_currency
        
        try:
            # Create product
            product = stripe.Product.create(
                name=name,
                type='service',
                stripe_account=stripe_account
            )
            
            # Create price
            stripe_price = stripe.Price.create(
                unit_amount=int(price * 100),
                currency=currency,
                recurring={"interval": interval},
                product=product.id,
                stripe_account=stripe_account
            )
            
            return {
                'product_id': product.id,
                'price_id': stripe_price.id,
                'name': name,
                'price': price,
                'currency': currency,
                'interval': interval
            }
        except stripe.error.StripeError as e:
            self.log_error('create_plan', str(e))
            return None
    
    def create_subscription(self, customer_id, price_id, user_id, metadata=None):
        """Create a new subscription for a customer"""
        try:
            subscription = stripe.Subscription.create(
                customer=customer_id,
                items=[{"price": price_id}],
                trial_period_days=self.trial_period_days,
                metadata={
                    'user_id': user_id,
                    **(metadata or {})
                },
                payment_behavior='default_incomplete',
                expand=['latest_invoice.payment_intent'],
                stripe_account=stripe_account
            )
            
            # Update user subscription status in database
            self.update_user_subscription(
                user_id,
                subscription.id,
                'trialing',
                subscription.trial_end
            )
            
            return subscription
        except stripe.error.StripeError as e:
            self.log_error('create_subscription', str(e))
            return None
    
    def cancel_subscription(self, subscription_id):
        """Cancel a subscription"""
        try:
            subscription = stripe.Subscription.modify(
                subscription_id,
                cancel_at_period_end=True,
                stripe_account=stripe_account
            )
            
            # Get user ID from metadata
            user_id = subscription.metadata.get('user_id')
            
            # Update user subscription status in database
            if user_id:
                self.update_user_subscription(
                    user_id,
                    subscription_id,
                    'pending_cancelation',
                    subscription.current_period_end
                )
            
            return subscription
        except stripe.error.StripeError as e:
            self.log_error('cancel_subscription', str(e))
            return None
    
    def reactivate_subscription(self, subscription_id):
        """Reactivate a canceled subscription"""
        try:
            subscription = stripe.Subscription.modify(
                subscription_id,
                cancel_at_period_end=False,
                stripe_account=stripe_account
            )
            
            # Get user ID from metadata
            user_id = subscription.metadata.get('user_id')
            
            # Update user subscription status in database
            if user_id:
                self.update_user_subscription(
                    user_id,
                    subscription_id,
                    'active',
                    subscription.current_period_end
                )
            
            return subscription
        except stripe.error.StripeError as e:
            self.log_error('reactivate_subscription', str(e))
            return None
    
    def update_subscription_plan(self, subscription_id, new_price_id):
        """Change a subscription's plan"""
        try:
            subscription = stripe.Subscription.retrieve(
                subscription_id,
                stripe_account=stripe_account
            )
            
            # Update subscription
            updated = stripe.Subscription.modify(
                subscription_id,
                items=[{
                    'id': subscription['items']['data'][0].id,
                    'price': new_price_id,
                }],
                stripe_account=stripe_account
            )
            
            # Get user ID from metadata
            user_id = subscription.metadata.get('user_id')
            
            # Update user subscription in database
            if user_id:
                self.update_user_subscription(
                    user_id,
                    subscription_id,
                    'active',
                    updated.current_period_end
                )
            
            return updated
        except stripe.error.StripeError as e:
            self.log_error('update_plan', str(e))
            return None
    
    def get_subscription(self, subscription_id):
        """Retrieve subscription details"""
        try:
            return stripe.Subscription.retrieve(
                subscription_id,
                stripe_account=stripe_account
            )
        except stripe.error.StripeError as e:
            self.log_error('get_subscription', str(e))
            return None
    
    def list_user_subscriptions(self, user_id):
        """List all subscriptions for a user"""
        try:
            subscriptions = stripe.Subscription.list(
                stripe_account=stripe_account,
                limit=100,
                status='all'
            )
            
            # Filter by user ID in metadata
            user_subs = [
                sub for sub in subscriptions.auto_paging_iter()
                if sub.metadata.get('user_id') == user_id
            ]
            
            return user_subs
        except stripe.error.StripeError as e:
            self.log_error('list_subscriptions', str(e))
            return []
    
    def update_user_subscription(self, user_id, subscription_id, status, end_date=None):
        """Update subscription status in database (stub implementation)"""
        print(f"Updating subscription {subscription_id} for user {user_id}: {status}")
        # Implement actual database update
        # Should store: user_id, subscription_id, status, plan_id, start_date, end_date
    
    def handle_failed_payment(self, subscription):
        """Handle failed subscription payments"""
        user_id = subscription.metadata.get('user_id')
        if not user_id:
            return
        
        # Notify user
        self.notify_user(
            user_id,
            "Payment Failed",
            "Your subscription payment failed. Please update your payment method."
        )
        
        # Update subscription status
        self.update_user_subscription(
            user_id,
            subscription.id,
            'past_due'
        )
        
        # Retry logic
        if subscription.attempt_count < 3:
            # Stripe automatically retries
            return
        
        # Cancel subscription after 3 failed attempts
        self.cancel_subscription(subscription.id)
        self.notify_user(
            user_id,
            "Subscription Canceled",
            "Your subscription has been canceled due to multiple failed payments."
        )
    
    def notify_user(self, user_id, subject, message):
        """Send notification to user (stub implementation)"""
        print(f"Notification to {user_id}: [{subject}] {message}")
        # Implement actual notification system (email, in-app, etc.)
    
    def log_error(self, context, message):
        """Log subscription errors"""
        timestamp = datetime.utcnow().isoformat()
        error_data = {
            'context': context,
            'message': message,
            'timestamp': timestamp
        }
        with open("subscription_errors.log", "a") as f:
            f.write(json.dumps(error_data) + "\n")
    
    def apply_coupon(self, subscription_id, coupon_id):
        """Apply coupon to a subscription"""
        try:
            subscription = stripe.Subscription.modify(
                subscription_id,
                coupon=coupon_id,
                stripe_account=stripe_account
            )
            return subscription
        except stripe.error.StripeError as e:
            self.log_error('apply_coupon', str(e))
            return None
    
    def create_usage_record(self, subscription_item_id, quantity, timestamp=None):
        """Record usage for metered billing"""
        try:
            timestamp = timestamp or int(time.time())
            record = stripe.SubscriptionItem.create_usage_record(
                subscription_item_id,
                quantity=quantity,
                timestamp=timestamp,
                stripe_account=stripe_account
            )
            return record
        except stripe.error.StripeError as e:
            self.log_error('create_usage_record', str(e))
            return None

# Singleton instance for easy access
subscription_manager = SubscriptionManager()
