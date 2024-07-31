import boto3
import os
import pandas as pd
from joblib import dump
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
import logging

# S3 configuration
bucket_name = 'stock-market-project'
data_file_key = 'data/NVDA_stock_data.xlsx'
model_file_key = 'model/model.joblib'
local_data_path = 'NVDA_stock_data.xlsx'
local_model_path = 'model.joblib'

s3 = boto3.client('s3')

# Set up logging
logging.basicConfig(filename='train_model.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def download_from_s3(file_key, local_path):
    logging.info(f'Downloading {file_key} from S3 to {local_path}.')
    s3.download_file(bucket_name, file_key, local_path)
    logging.info('Download complete.')

def upload_to_s3(file_key, local_path):
    logging.info(f'Uploading {local_path} to S3 as {file_key}.')
    s3.upload_file(local_path, bucket_name, file_key)
    logging.info('Upload complete.')

def retrain_model():
    logging.info('Retraining model...')
    data = pd.read_excel(local_data_path)
    X = data[['open', 'high', 'low']]
    y = data['close']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
    logging.info('Fitting the model.')
    rf_model.fit(X_train, y_train)

    dump(rf_model, local_model_path)
    logging.info(f'Model saved to {local_model_path}.')
    upload_to_s3(model_file_key, local_model_path)
    logging.info('Model retrained and uploaded to S3.')

def main():
    logging.info('Starting model retraining process.')
    download_from_s3(data_file_key, local_data_path)
    retrain_model()
    logging.info('Model retraining process completed.')

if __name__ == '__main__':
    main()
