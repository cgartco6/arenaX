import requests
import os
import time
import json
from dotenv import load_dotenv

load_dotenv()

FRAUD_MODEL_API = "https://api-inference.huggingface.co/models/elastic/distilbert-base-uncased-finetuned-conll03-english"
HEADERS = {"Authorization": f"Bearer {os.getenv('HF_TOKEN')}"}

def detect_fraud(transaction):
    """Use AI model to detect fraudulent transactions"""
    payload = {
        "inputs": f"""
        Analyze this transaction for fraud risk:
        Amount: {transaction['amount']} {transaction['currency']}
        User ID: {transaction['user_id']}
        IP: {transaction['ip']}
        Country: {transaction['country']}
        Device: {transaction['device']}
        """
    }
    
    response = requests.post(FRAUD_MODEL_API, headers=HEADERS, json=payload)
    result = response.json()
    
    # Extract fraud probability
    fraud_score = 0.0
    for item in result:
        if 'label' in item and item['label'] == 'fraud':
            fraud_score = item['score']
            break
    
    return fraud_score > 0.85

def monitor_transactions():
    """Continuously monitor transactions"""
    while True:
        try:
            # Get recent transactions (pseudo-code)
            transactions = get_recent_transactions()
            
            for transaction in transactions:
                if detect_fraud(transaction):
                    block_transaction(transaction['id'])
                    alert_admin(transaction)
            
            time.sleep(300)  # Check every 5 minutes
        except Exception as e:
            print(f"Monitoring error: {str(e)}")
            time.sleep(60)

def block_transaction(transaction_id):
    """Block a fraudulent transaction"""
    print(f"Blocking transaction {transaction_id}")
    # Implement actual blocking logic

def alert_admin(transaction):
    """Send alert to admin"""
    print(f"ALERT: Fraud detected in transaction {transaction['id']}")
    # Implement actual alert system

def get_recent_transactions():
    """Retrieve recent transactions (stub implementation)"""
    # This would connect to your database in production
    return []
