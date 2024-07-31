from flask import Flask, render_template, request
import requests
from joblib import load
import pandas as pd
import os
import plotly.graph_objs as go
import plotly.offline as pyo
from datetime import datetime, timedelta
import boto3

app = Flask(__name__)

api_key = os.getenv('ALPHA_API_KEY')
s3 = boto3.client('s3')
bucket_name = 'stock-market-project'
data_file_key = 'data/NVDA_stock_data.xlsx'
model_file_key = 'model/model.joblib'

local_model_path = 'model.joblib'
local_data_path = 'NVDA_stock_data.xlsx'

def download_from_s3(file_key, local_path):
    s3.download_file(bucket_name, file_key, local_path)

def load_model():
    if not os.path.exists(local_model_path) or is_model_file_outdated(local_model_path):
        download_from_s3(model_file_key, local_model_path)
    return load(local_model_path)

def load_data():
    if not os.path.exists(local_data_path) or is_file_outdated(local_data_path):
        download_from_s3(data_file_key, local_data_path)
    return pd.read_excel(local_data_path)

def is_model_file_outdated(file_path):
    # Check if the file is older than 4 days
    return (datetime.now() - datetime.fromtimestamp(os.path.getmtime(file_path))) > timedelta(days=4)

def is_file_outdated(file_path):
    # Check if the file is older than 1 day
    return (datetime.now() - datetime.fromtimestamp(os.path.getmtime(file_path))) > timedelta(days=1)

model = load_model()
data = load_data()

@app.route('/')
def home():
    graph = create_graph()
    return render_template('index.html', graph=graph)

def create_graph():
    df = pd.read_excel(local_data_path)  
    trace_close = go.Scatter(x=df['date'], y=df['close'], mode='lines', name='Close Price', 
                             line=dict(color='blue', width=2))
    trace_high = go.Scatter(x=df['date'], y=df['high'], mode='lines', name='High Price', 
                            line=dict(color='green', width=1, dash='dash'))
    trace_low = go.Scatter(x=df['date'], y=df['low'], mode='lines', name='Low Price', 
                           line=dict(color='red', width=1, dash='dash'))

    data_traces = [trace_close, trace_high, trace_low]

    layout = go.Layout(
        title='NVDA Stock Price',
        xaxis=dict(title='Date', rangeslider=dict(visible=True), type='date'),
        yaxis=dict(title='Price (USD)', tickprefix='$'),
        hovermode='x unified',
        legend=dict(x=0, y=1, traceorder='normal'),
        template='plotly_white'
    )

    fig = go.Figure(data=data_traces, layout=layout)
    graph = pyo.plot(fig, include_plotlyjs=False, output_type='div')
    return graph

@app.route('/predict', methods=['POST'])
def predict():
    features = [float(x) for x in request.form.values()]
    final_features = [pd.Series(features)]
    prediction = model.predict(final_features)
    output = round(prediction[0], 2)
    graph = create_graph()
    return render_template('index.html', prediction_text=f'Predicted Stock Close Price: ${output}', graph=graph)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
