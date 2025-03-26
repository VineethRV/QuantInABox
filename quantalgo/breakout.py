import numpy as np
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt

def fetch_pair_data(stock1, stock2, period="6mo"):
    """Fetch historical stock data for two stocks and compute spread & Z-score."""
    df1 = yf.Ticker(stock1).history(period=period)["Close"]
    df2 = yf.Ticker(stock2).history(period=period)["Close"]

    df = pd.DataFrame({stock1: df1, stock2: df2})
    df.dropna(inplace=True)  # Remove NaNs to avoid errors

    # Compute spread
    df["Spread"] = df[stock1] - df[stock2]
    df["Spread_Mean"] = df["Spread"].rolling(window=30).mean()
    df["Spread_Std"] = df["Spread"].rolling(window=30).std()

    # Compute Z-Score
    df["Z-Score"] = (df["Spread"] - df["Spread_Mean"]) / df["Spread_Std"]

    return df

def pairs_trading_strategy(df, entry_threshold=2, exit_threshold=0.5):
    """Generate trading signals based on Z-score thresholds."""
    df["Signal"] = np.where(df["Z-Score"] > entry_threshold, -1, 
                        np.where(df["Z-Score"] < -entry_threshold, 1, 0))

    return df

def backtest_pairs_trading(df, capital=100000):
    """Simulate pairs trading strategy and calculate portfolio performance."""
    position = 0
    cash = capital
    df["Portfolio"] = capital

    for i in range(1, len(df)):
        if df["Signal"].iloc[i] == 1 and position == 0:  # Long spread
            position = cash // df["Spread"].iloc[i]
            cash -= position * df["Spread"].iloc[i]

        elif df["Signal"].iloc[i] == -1 and position == 0:  # Short spread
            position = cash // df["Spread"].iloc[i]
            cash += position * df["Spread"].iloc[i]

        elif df["Signal"].iloc[i] == 0 and position != 0:  # Exit trade
            cash += position * df["Spread"].iloc[i]
            position = 0

        df["Portfolio"].iloc[i] = cash + (position * df["Spread"].iloc[i])

    return df

# Fetch and process data for TCS & INFY
df = fetch_pair_data("TCS.NS", "INFY.NS")
df = pairs_trading_strategy(df)
df = backtest_pairs_trading(df)

# Plot Spread with Z-Score bands
plt.figure(figsize=(12,6))
plt.plot(df.index, df["Spread"], label="Spread", color="blue")
plt.axhline(df["Spread"].mean(), color="black", linestyle="--", label="Mean Spread")
plt.axhline(df["Spread"].mean() + 2*df["Spread_Std"].mean(), color="red", linestyle="--", label="Upper Band")
plt.axhline(df["Spread"].mean() - 2*df["Spread_Std"].mean(), color="green", linestyle="--", label="Lower Band")
plt.scatter(df[df["Signal"] == 1].index, df[df["Signal"] == 1]["Spread"], marker="^", color="green", label="Long Signal", alpha=1)
plt.scatter(df[df["Signal"] == -1].index, df[df["Signal"] == -1]["Spread"], marker="v", color="red", label="Short Signal", alpha=1)
plt.title("Pairs Trading Strategy (TCS vs INFY)")
plt.legend()
plt.show()

# Plot Portfolio Performance
plt.figure(figsize=(12,6))
plt.plot(df.index, df["Portfolio"], label="Portfolio Value", color="purple")
plt.title("Pairs Trading Portfolio Performance")
plt.xlabel("Date")
plt.ylabel("Portfolio Value (₹)")
plt.legend()
plt.show()

print(f"Final Portfolio Value: ₹{df['Portfolio'].iloc[-1]:,.2f}")
