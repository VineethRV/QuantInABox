import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def fetch_data(symbol, period="6mo"):
    stock = yf.Ticker(symbol)
    df = stock.history(period=period)
    return df

def mean_reversion_strategy(df, window=20):
    df['SMA'] = df['Close'].rolling(window=window).mean()
    df['StdDev'] = df['Close'].rolling(window=window).std()
    df['UpperBand'] = df['SMA'] + (2 * df['StdDev'])
    df['LowerBand'] = df['SMA'] - (2 * df['StdDev'])

    # Buy when price goes below lower band, Sell when it goes above upper band
    df['Signal'] = np.where(df['Close'] < df['LowerBand'], 1, 
                            np.where(df['Close'] > df['UpperBand'], -1, 0))

    return df

def backtest(df, initial_capital=100000):
    capital = initial_capital
    position = 0  # Number of shares
    buy_price = 0  # Track buy price

    df["Portfolio"] = capital
    for i in range(1, len(df)):
        if df['Signal'].iloc[i] == 1:  # Buy
            position = capital // df['Close'].iloc[i]
            buy_price = df['Close'].iloc[i]
            capital -= position * buy_price
        elif df['Signal'].iloc[i] == -1 and position > 0:  # Sell
            capital += position * df['Close'].iloc[i]
            position = 0
        df["Portfolio"].iloc[i] = capital + (position * df['Close'].iloc[i])

    return df

def plot_strategy(df):
    plt.figure(figsize=(12,6))
    plt.plot(df.index, df["Close"], label="Stock Price", color='blue')
    plt.plot(df.index, df["UpperBand"], label="Upper Band", linestyle="--", color='red')
    plt.plot(df.index, df["LowerBand"], label="Lower Band", linestyle="--", color='green')
    
    buy_signals = df[df['Signal'] == 1]
    sell_signals = df[df['Signal'] == -1]
    
    plt.scatter(buy_signals.index, buy_signals["Close"], marker="^", color="green", label="Buy Signal", alpha=1)
    plt.scatter(sell_signals.index, sell_signals["Close"], marker="v", color="red", label="Sell Signal", alpha=1)

    plt.title("Mean Reversion Strategy")
    plt.legend()
    plt.show()

# Example Usage
symbol = "TSLA"  # Use NSE ticker symbols
df = fetch_data(symbol)
df = mean_reversion_strategy(df)
df = backtest(df)

print(f"Final Portfolio Value: ₹{df['Portfolio'].iloc[-1]:,.2f}")

plot_strategy(df)
