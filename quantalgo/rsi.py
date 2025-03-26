import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def fetch_data(symbol, period="6mo"):
    stock = yf.Ticker(symbol)
    df = stock.history(period=period)
    return df

def compute_rsi(df, period=14):
    delta = df["Close"].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()

    rs = gain / loss
    df["RSI"] = 100 - (100 / (1 + rs))
    return df

def rsi_strategy(df):
    df["Signal"] = np.where(df["RSI"] < 30, 1, np.where(df["RSI"] > 70, -1, 0))
    return df

df = fetch_data("TCS.NS")
df = compute_rsi(df)
df = rsi_strategy(df)

plt.figure(figsize=(12,6))
plt.plot(df.index, df["Close"], label="Stock Price")
plt.scatter(df[df["Signal"] == 1].index, df[df["Signal"] == 1]["Close"], marker="^", color="green", label="Buy Signal", alpha=1)
plt.scatter(df[df["Signal"] == -1].index, df[df["Signal"] == -1]["Close"], marker="v", color="red", label="Sell Signal", alpha=1)
plt.title("RSI Mean Reversion Strategy")
plt.legend()
plt.show()
