from flask import Flask, render_template, request
import requests
from joblib import load
import pandas as pd
import os
import plotly.graph_objs as go
import plotly.offline as pyo
from datetime import datetime, timedelta

app = Flask(__name__)
api_key = os.getenv('ALPHA_API_KEY')
model = load('model.joblib')


@app.route('/')
def home():
    data = get_stock_data('NVDA')
    graphs = create_graphs(data)
    return render_template('index.html', graphs=graphs)


def get_stock_data(symbol):
    url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&outputsize=full&apikey={api_key}'
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        try:
            time_series_data = data['Time Series (Daily)']
        except KeyError:
            try:
                if 'Error' in data:
                    print(f"Error message from Alpha Vantage API: {data['Information']}")
                    exit(1)

                time_series_data = data['Default Response']
            except KeyError:
                print("Unexpected response format from Alpha Vantage API. Please update the code to handle the new format.")
                exit(1)

        df = pd.DataFrame.from_dict(time_series_data, orient='index')
        df = df[['1. open', '2. high', '3. low', '4. close', '5. volume']]
        df = df.reset_index(drop=False).rename(columns={
            'index': 'date', '1. open': 'open', '2. high': 'high', '3. low': 'low', '4. close': 'close', '5. volume': 'volume'
        })
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date')

        # Filter data for the last 60 days
        last_60_days = datetime.now() - timedelta(days=60)
        df = df[df['date'] >= last_60_days]

        filename = 'NVDA_stock_data.xlsx'
        df.to_excel(filename, index=False)
        print(f"Data successfully saved to {filename}")
        return df
    else:
        print(f"Error fetching data: {response.status_code}")
        return pd.DataFrame()


def create_graphs(df):
    graphs = []
    traces = {
        'open': 'Open Price',
        'high': 'High Price',
        'low': 'Low Price',
        'close': 'Close Price'
    }
    for column, title in traces.items():
        trace = go.Scatter(x=df['date'], y=df[column], mode='lines', name=title)
        data = [trace]
        layout = go.Layout(title=title, xaxis=dict(title='Date'), yaxis=dict(title=title))
        fig = go.Figure(data=data, layout=layout)
        graph = pyo.plot(fig, include_plotlyjs=False, output_type='div')
        graphs.append(graph)

    return graphs


@app.route('/predict', methods=['POST'])
def predict():
    features = [float(x) for x in request.form.values()]
    final_features = [pd.Series(features)]
    prediction = model.predict(final_features)
    output = round(prediction[0], 2)
    data = get_stock_data('NVDA')
    graphs = create_graphs(data)
    return render_template('index.html', prediction_text=f'Predicted Stock Close Price: ${output}', graphs=graphs)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
