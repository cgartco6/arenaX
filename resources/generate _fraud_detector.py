import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.models import save_model
import joblib

# Generate synthetic fraud dataset
def generate_fraud_data(num_samples=10000):
    np.random.seed(42)
    
    # Features: transaction amount, time, location, frequency, etc.
    data = {
        'amount': np.random.exponential(100, num_samples),
        'time_of_day': np.random.randint(0, 24, num_samples),
        'day_of_week': np.random.randint(0, 7, num_samples),
        'merchant_category': np.random.randint(0, 10, num_samples),
        'customer_history': np.random.poisson(5, num_samples),
        'device_type': np.random.choice([0, 1, 2], num_samples),
        'location_mismatch': np.random.choice([0, 1], num_samples, p=[0.7, 0.3]),
        'ip_risk_score': np.random.beta(0.5, 0.5, num_samples)
    }
    
    df = pd.DataFrame(data)
    
    # Fraud rules (synthetic patterns)
    fraud_conditions = (
        (df['amount'] > 500) & 
        (df['location_mismatch'] == 1) &
        (df['ip_risk_score'] > 0.8)
    ) | (
        (df['amount'] > 300) & 
        (df['time_of_day'] < 6) & 
        (df['merchant_category'] == 3)
    ) | (
        (df['customer_history'] < 2) & 
        (df['amount'] > 700)
    )
    
    df['is_fraud'] = fraud_conditions.astype(int)
    
    # Add noise
    fraud_indices = df[df['is_fraud'] == 1].index
    df.loc[fraud_indices[:len(fraud_indices)//3], 'is_fraud'] = 0
    
    non_fraud_indices = df[df['is_fraud'] == 0].index
    df.loc[non_fraud_indices[:200], 'is_fraud'] = 1
    
    return df

# Create and train fraud detection model
def create_fraud_detection_model():
    # Generate data
    df = generate_fraud_data()
    
    # Preprocess data
    X = df.drop('is_fraud', axis=1)
    y = df['is_fraud']
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=42
    )
    
    # Scale features
    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_test = scaler.transform(X_test)
    
    # Save scaler
    joblib.dump(scaler, 'fraud_scaler.pkl')
    
    # Create model
    model = Sequential([
        Dense(64, input_dim=X_train.shape[1], activation='relu'),
        Dropout(0.3),
        Dense(32, activation='relu'),
        Dropout(0.2),
        Dense(16, activation='relu'),
        Dense(1, activation='sigmoid')
    ])
    
    # Compile model
    model.compile(
        optimizer=Adam(learning_rate=0.001),
        loss='binary_crossentropy',
        metrics=['accuracy', 'Precision', 'Recall']
    )
    
    # Train model
    history = model.fit(
        X_train, y_train,
        validation_data=(X_test, y_test),
        epochs=15,
        batch_size=64,
        class_weight={0: 1, 1: 10}  # Weight fraud class higher
    )
    
    return model, history

if __name__ == "__main__":
    # Create and save model
    model, history = create_fraud_detection_model()
    save_model(model, 'fraud
