import streamlit as st
from streamlit_oauth import OAuth2Component
import requests
import pandas as pd
from datetime import datetime

# ------------------- CONFIG -------------------
API_KEY = "YOUR_ALPHA_VANTAGE_API_KEY"
client_id = "YOUR_GOOGLE_CLIENT_ID"
client_secret = "YOUR_GOOGLE_CLIENT_SECRET"
redirect_uri = "http://localhost:8501"  # or your Streamlit Cloud URL

# ------------------- STOCKS -------------------
stocks = {
    "Tata Motors": "TATAMOTORS.NS",
    "Tata Steel": "TATASTEEL.NS",
    "Reliance": "RELIANCE.NS",
    "Garuda (mock)": None,
    "Vishal Mega Mart (mock)": None
}

# ------------------- GOOGLE AUTH -------------------
oauth = OAuth2Component(
    client_id=client_id,
    client_secret=client_secret,
    authorize_endpoint="https://accounts.google.com/o/oauth2/auth",
    token_endpoint="https://oauth2.googleapis.com/token",
    revoke_endpoint="https://oauth2.googleapis.com/revoke",
)

def fetch_stock_data(symbol):
    base_url = "https://www.alphavantage.co/query"
    params = {
        "function": "TIME_SERIES_DAILY_ADJUSTED",
        "symbol": symbol,
        "outputsize": "compact",
        "apikey": API_KEY
    }
    response = requests.get(base_url, params=params)
    data = response.json()
    try:
        timeseries = data["Time Series (Daily)"]
        df = pd.DataFrame.from_dict(timeseries, orient="index", dtype=float)
        df = df.rename(columns={
            "1. open": "Open",
            "2. high": "High",
            "3. low": "Low",
            "4. close": "Close",
            "5. adjusted close": "Adj Close",
            "6. volume": "Volume"
        })
        df.index = pd.to_datetime(df.index)
        df.sort_index(inplace=True)
        return df
    except KeyError:
        return None

# ------------------- STREAMLIT UI -------------------
st.set_page_config(page_title="📊 Stock Workshop Dashboard")
st.title("📈 Stock Market Workshop Dashboard")

# ------------------- LOGIN HANDLING -------------------
if "token" not in st.session_state:
    result = oauth.authorize_button(
        name="Continue with Google",
        icon="🌐",
        redirect_uri=redirect_uri,
        scope="openid email profile",
        key="google",
    )
    if result:
        st.session_state.token = result["token"]
        st.rerun()
else:
    # Get user info
    user_info = requests.get(
        "https://www.googleapis.com/oauth2/v1/userinfo",
        headers={"Authorization": f"Bearer {st.session_state.token['access_token']}"},
    ).json()

    st.success(f"Welcome, {user_info['name']} ({user_info['email']})")

    if st.button("Logout"):
        del st.session_state["token"]
        st.rerun()

    # ------------------- DASHBOARD -------------------
    st.header("📊 Select a Stock")
    stock_choice = st.selectbox("Choose Stock", list(stocks.keys()))
    symbol = stocks[stock_choice]

    if symbol:
        data = fetch_stock_data(symbol)
        if data is not None:
            st.subheader(f"{stock_choice} - Adjusted Close Prices")
            st.line_chart(data['Adj Close'])
            st.subheader("📅 Recent 10 Days Data")
            st.dataframe(data.tail(10))
        else:
            st.error("⚠️ Failed to fetch data. Check API key or API limit.")
    else:
        st.warning(f"{stock_choice} not available in Alpha Vantage. Showing mock data.")
        mock_data = pd.DataFrame({
            "Date": pd.date_range(end=datetime.today(), periods=10),
            "Price": [100 + i * 2 for i in range(10)]
        })
        mock_data.set_index("Date", inplace=True)
        st.line_chart(mock_data["Price"])
        st.dataframe(mock_data)
