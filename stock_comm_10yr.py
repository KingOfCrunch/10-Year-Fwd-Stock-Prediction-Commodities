import streamlit as st
import pandas as pd
import requests

# --- 1. Get PPIACO data from FRED ---
def get_fred_ppiaco(api_key):
    url = "https://api.stlouisfed.org/fred/series/observations"
    params = {
        "series_id": "PPIACO",
        "api_key": "2b974d0cfdaa48c443b89eda76d65215",
        "file_type": "json",
        "frequency": "m"
    }
    r = requests.get(url, params=params)
    data = r.json()
    df = pd.DataFrame(data['observations'])
    df['date'] = pd.to_datetime(df['date'])
    df['value'] = pd.to_numeric(df['value'], errors='coerce')
    return df[['date', 'value']].rename(columns={'value': 'PPIACO'})

# --- 2. Get Shiller S&P data from XLS ---
def get_shiller_data(xls_url):
    df = pd.read_excel(xls_url, skiprows=7)  # Skip explainer rows
    df = df.iloc[:, :2]  # Keep only first two columns
    df.columns = ['Date', 'S&P Comp. P']
    # Parse date
    df['Date'] = df['Date'].astype(str)
    df = df[df['Date'].str.contains(r'^\d{4}\.\d{2}$')]  # Only rows with YYYY.MM
    df['date'] = pd.to_datetime(df['Date'], format='%Y.%m')
    df['S&P Comp. P'] = pd.to_numeric(df['S&P Comp. P'], errors='coerce')
    return df[['date', 'S&P Comp. P']]

# --- 3. Streamlit App ---
st.title("S&P vs PPIACO Line Chart")

api_key = "2b974d0cfdaa48c443b89eda76d65215"
fred_df = get_fred_ppiaco(api_key)
shiller_url = "https://img1.wsimg.com/blobby/go/e5e77e0b-59d1-44d9-ab25-4763ac982e53/downloads/f0faea35-265f-48c9-b948-d427e2c8adf7/ie_data.xls"
shiller_df = get_shiller_data(shiller_url)

# Merge on date
merged = pd.merge(shiller_df, fred_df, on='date', how='inner')

# Plot
import matplotlib.pyplot as plt
fig, ax1 = plt.subplots()
ax1.plot(merged['date'], merged['S&P Comp. P'], color='blue', label='S&P Comp. P')
ax1.set_ylabel('S&P Comp. P', color='blue')
ax2 = ax1.twinx()
ax2.plot(merged['date'], merged['PPIACO'], color='red', label='PPIACO')
ax2.set_ylabel('PPIACO', color='red')
st.pyplot(fig)
