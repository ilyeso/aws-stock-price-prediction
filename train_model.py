import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from joblib import dump

# Data Loading
data = pd.read_excel('NVDA_stock_data.xlsx')  

# Data preparation for training
X = data[['open', 'high', 'low', 'volume']]  # Features
y = data['close']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train the model
rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
rf_model.fit(X_train, y_train)

# Save the model
dump(rf_model, 'model.joblib')
