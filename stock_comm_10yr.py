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
    df = pd.read_excel(xls_url, skiprows=7, engine="xlrd", sheet_name="Data")  # Skip explainer rows, specify engine for .xls and sheet name
    print("Columns in XLS:", df.columns.tolist())  # Debug print, will show in Streamlit terminal/logs
    # Use 'Date' and 'P' columns, rename 'P' to 'S&P Comp. P'
    # Robust column selection by partial match
    date_col = next((col for col in df.columns if 'Date' in col), df.columns[0])
    p_col = next((col for col in df.columns if col.strip() == 'P'), None)
    if not p_col:
        # fallback: use second column if 'P' not found
        p_col = df.columns[1]
    df = df.loc[:, [date_col, p_col]]
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

# Interactive Plotly chart
import plotly.graph_objects as go
fig = go.Figure()
fig.add_trace(go.Scatter(x=merged['date'], y=merged['S&P Comp. P'], name='S&P Comp. P', yaxis='y1', mode='lines+markers', line=dict(color='blue'), marker=dict(color='blue'), hovertemplate='Date: %{x}<br>S&P Comp. P: %{y:.2f}<extra></extra>'))
fig.add_trace(go.Scatter(x=merged['date'], y=merged['PPIACO'], name='PPIACO', yaxis='y2', mode='lines+markers', line=dict(color='red'), marker=dict(color='red'), hovertemplate='Date: %{x}<br>PPIACO: %{y:.2f}<extra></extra>'))
fig.update_layout(
    xaxis=dict(title='Date'),
    yaxis=dict(title='S&P Comp. P', titlefont=dict(color='blue'), tickfont=dict(color='blue')),
    yaxis2=dict(title='PPIACO', titlefont=dict(color='red'), tickfont=dict(color='red'), overlaying='y', side='right'),
    legend=dict(x=0.01, y=0.99),
    hovermode='x unified',
    margin=dict(l=40, r=40, t=40, b=40)
)
st.plotly_chart(fig, use_container_width=True)
