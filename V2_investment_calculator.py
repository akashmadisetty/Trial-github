import streamlit as st
import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import yfinance as yf
from bs4 import BeautifulSoup

def fetch_gold_price():
    """
    Fetches gold price data from a financial data provider.
    """
    try:
        # Fetch real gold prices from the goldapi.io API
        url = "https://www.goldapi.io/api/XAU/INR"
        headers = {"x-access-token": "API_KEY"}  # Replace 'YOUR_API_KEY' with your actual API key
        response = requests.get(url, headers=headers)
        data = response.json()
        gold_price = data["price"]
        return gold_price
    except Exception as e:
        st.error(f"Error fetching gold price data: {str(e)}")
        return None

def fetch_fd_interest_rates():
    # Fixed interest rate of 7.5% for all tenures
    rates = {"SBI": {"1 Year": 7.5, "2 Years": 7.5, "3 Years": 7.5}}
    return rates

def fetch_nifty50_data():
    try:
        nifty_data = yf.download("^NSEI", start=datetime.now() - timedelta(days=365), end=datetime.now())
        return nifty_data
    except Exception as e:
        st.error(f"Error fetching Nifty 50 data: {str(e)}")
        return None

def calculate_returns(investment_amounts, fd_rates, gold_price):
    gold_return = (investment_amounts["gold"] / gold_price) * (gold_price * 1.05)
    fd_returns = 0
    for bank, rates in fd_rates.items():
        for tenure, rate in rates.items():
            if tenure in investment_amounts["fd"][bank]:
                fd_returns += investment_amounts["fd"][bank][tenure] * (1 + rate / 100)
    nifty_return = investment_amounts["nifty50"] * 1.10
    total_investment = investment_amounts["gold"] + fd_returns + investment_amounts["nifty50"]
    total_return = gold_return + fd_returns + nifty_return
    return total_investment, total_return

def display_investment_allocation(investment_amounts):
    labels = ["Gold", "Fixed Deposits", "Nifty 50"]
    fd_total = sum(sum(amounts.values()) for amounts in investment_amounts["fd"].values())
    sizes = [investment_amounts["gold"], fd_total, investment_amounts["nifty50"]]
    colors = ["gold", "lightblue", "darkgreen"]
    plt.pie(sizes, labels=labels, colors=colors, autopct="%1.1f%%")
    st.pyplot(plt)

def investment_calculator():
    st.title("Investment Planning Assistant")
    
    # User input for investment amounts
    gold_investment = st.number_input("Gold investment", min_value=0.0)
    fd_investments = {
        "SBI": {
            "1 Year": st.number_input("SBI 1 Year FD investment", min_value=0.0),
            "2 Years": st.number_input("SBI 2 Years FD investment", min_value=0.0),
            "3 Years": st.number_input("SBI 3 Years FD investment", min_value=0.0),
        }
    }
    nifty50_investment = st.number_input("Nifty 50 investment", min_value=0.0)
    
    st.header("Current Gold Price")
    gold_price = fetch_gold_price()
    st.write(f"Gold Price: ₹{gold_price}")
    
    # Fixed Deposits (FDs) interest rates
    fd_rates = fetch_fd_interest_rates()
    st.header("Fixed Deposits Interest Rates")
    for bank, rates in fd_rates.items():
        st.subheader(f"{bank} FD Interest Rates")
        for tenure, rate in rates.items():
            st.write(f"{tenure}: {rate}%")
    
    # Stocks (Nifty 50) data
    nifty_data = fetch_nifty50_data()
    st.header("Nifty 50 Stocks Data")
    st.write(nifty_data)
    
    if st.button("Calculate Returns"):
        investment_amounts = {
            "gold": gold_investment,
            "fd": fd_investments,
            "nifty50": nifty50_investment,
        }
        
        total_investment, total_return = calculate_returns(investment_amounts, fd_rates, gold_price)
        st.write(f"Total investment: ₹{total_investment:,.2f}")
        st.write(f"Expected return: ₹{total_return:,.2f}")
        display_investment_allocation(investment_amounts)

if __name__ == "__main__":
    investment_calculator()
