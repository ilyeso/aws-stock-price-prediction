import requests
import pandas as pd

api_key = 'PVSRG7VDL6NM4MWK'

url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=NVDA&outputsize=full&apikey={api_key}'
response = requests.get(url)

if response.status_code == 200:
  data = response.json()

# Handle different data structures based on Alpha Vantage API response format
try:
  # Extract the time series data dictionary (assuming standard format)
  time_series_data = data['Time Series (Daily)']
except KeyError:
  # Handle potential API response changes (alternative format)
  try:
      # Check for "Information" key indicating an error message
      if 'Error' in data:
          print(
              f"Error message from Alpha Vantage API: {data['Information']}")
          exit(1)  # Exit gracefully if API returns an error

      # Extract data from a different key based on API updates
      time_series_data = data['Default Response']
  except KeyError:
      print(
          "Unexpected response format from Alpha Vantage API. Please update the code to handle the new format.")
      exit(1)  # Exit gracefully if format changes unexpectedly

df = pd.DataFrame.from_dict(time_series_data, orient='index')

# Reorder columns to ensure consistent structure
df = df[['1. open', '2. high', '3. low', '4. close', '5. volume']]

# Set the index (date) as the first column
df = df.reset_index(drop=False).rename(columns={
  'index': 'date', '1. open': 'open', '2. high': 'high', '3. low': 'low', '4. close': 'close', '5. volume': 'volume'})

# Convert date column to datetime format (optional)
df['date'] = pd.to_datetime(df['date'])

# Write the DataFrame to an Excel file
filename = 'NVDA_stock_data.xlsx'
# Set index=False to avoid index column in Excel
df.to_excel(filename, index=False)
print(f"Data successfully saved to {filename}")