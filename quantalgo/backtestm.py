import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def fetch_data(symbol, period="2y"):
    """Fetch extended historical stock data."""
    try:
        stock = yf.Ticker(symbol)
        df = stock.history(period=period)
        
        if df.empty:
            raise ValueError(f"No data retrieved for {symbol}")
        
        return df
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None

def calculate_advanced_indicators(df, 
                                  short_window=10, 
                                  long_window=50, 
                                  rsi_window=14,
                                  macd_short=12,
                                  macd_long=26,
                                  macd_signal=9):
    """
    Calculate multiple technical indicators for more robust trading signals.
    
    Added indicators:
    - MACD (Moving Average Convergence Divergence)
    - Enhanced RSI and SMA logic
    """
    df = df.copy()
    
    # Simple Moving Averages
    df['SMA_Short'] = df['Close'].rolling(window=short_window, min_periods=1).mean()
    df['SMA_Long'] = df['Close'].rolling(window=long_window, min_periods=1).mean()
    
    # RSI with more nuanced calculation
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=rsi_window, min_periods=1).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=rsi_window, min_periods=1).mean()
    
    rs = gain / (loss + 1e-10)  # Prevent division by zero
    df['RSI'] = 100 - (100 / (1 + rs))
    
    # MACD Calculation
    exp1 = df['Close'].ewm(span=macd_short, adjust=False).mean()
    exp2 = df['Close'].ewm(span=macd_long, adjust=False).mean()
    df['MACD'] = exp1 - exp2
    df['MACD_Signal'] = df['MACD'].ewm(span=macd_signal, adjust=False).mean()
    
    # Advanced Signal Generation
    df['Signal'] = np.where(
        # Buy Conditions (more comprehensive)
        (df['SMA_Short'] > df['SMA_Long']) &  # Bullish moving average crossover
        (df['RSI'] > 50) &  # RSI above 50 (bullish momentum)
        (df['MACD'] > df['MACD_Signal']) &  # Bullish MACD
        (df['Close'] > df['SMA_Long']),  # Price above long-term moving average
        1,
        
        # Sell Conditions
        np.where(
            (df['SMA_Short'] < df['SMA_Long']) &  # Bearish moving average crossover
            (df['RSI'] < 50) &  # RSI below 50 (bearish momentum)
            (df['MACD'] < df['MACD_Signal']) &  # Bearish MACD
            (df['Close'] < df['SMA_Long']),  # Price below long-term moving average
            -1, 
            0  # Neutral
        )
    )
    
    return df

def backtest_with_adaptive_strategy(df, 
                                    initial_capital=100000, 
                                    risk_per_trade=0.02, 
                                    trailing_stop_loss_pct=0.05):
    """
    Advanced backtesting with:
    - Adaptive position sizing
    - Trailing stop loss
    - More sophisticated trade management
    """
    df = df.copy()
    cash = initial_capital
    shares = 0
    buy_price = 0
    max_portfolio_value = initial_capital
    trailing_stop = 0
    
    portfolio_values = [initial_capital]
    realized_gains = []
    
    for i in range(1, len(df)):
        current_price = df['Close'].iloc[i]
        prev_price = df['Close'].iloc[i-1]
        
        # Adaptive position sizing
        max_risk_amount = cash * risk_per_trade
        max_shares_to_buy = int(max_risk_amount / current_price)
        
        # Buy Signal
        if df['Signal'].iloc[i] == 1 and shares == 0:
            shares = max_shares_to_buy
            buy_price = current_price
            cash -= shares * buy_price
            trailing_stop = buy_price * (1 - trailing_stop_loss_pct)
        
        # Sell Conditions
        sell_condition = (
            # Explicit sell signal
            (df['Signal'].iloc[i] == -1) or 
            
            # Trailing stop loss triggered
            (shares > 0 and current_price <= trailing_stop)
        )
        
        # Sell Execution
        if sell_condition and shares > 0:
            sell_value = shares * current_price
            cash += sell_value
            
            # Track realized gains
            trade_profit = sell_value - (shares * buy_price)
            realized_gains.append(trade_profit)
            
            shares = 0
            buy_price = 0
            trailing_stop = 0
        
        # Update trailing stop if position is active
        if shares > 0:
            if current_price > buy_price * (1 + trailing_stop_loss_pct):
                trailing_stop = current_price * (1 - trailing_stop_loss_pct)
        
        # Calculate current portfolio value
        current_portfolio = cash + (shares * current_price)
        portfolio_values.append(current_portfolio)
        
        # Update max portfolio value for performance tracking
        max_portfolio_value = max(max_portfolio_value, current_portfolio)
    
    # Add tracking to DataFrame
    df['Portfolio_Value'] = portfolio_values
    
    return df, realized_gains

def plot_comprehensive_performance(df, symbol):
    """Enhanced performance visualization."""
    plt.figure(figsize=(15, 12))
    
    # Price and Technical Indicators
    plt.subplot(3, 1, 1)
    plt.title(f"{symbol} - Technical Analysis")
    plt.plot(df.index, df["Close"], label="Close Price", color='blue')
    plt.plot(df.index, df["SMA_Short"], label="Short SMA", linestyle="--", color='green')
    plt.plot(df.index, df["SMA_Long"], label="Long SMA", linestyle="--", color='red')
    plt.legend()
    
    # MACD and Signal
    plt.subplot(3, 1, 2)
    plt.title("MACD Indicator")
    plt.plot(df.index, df["MACD"], label="MACD", color='blue')
    plt.plot(df.index, df["MACD_Signal"], label="Signal Line", color='red')
    plt.legend()
    
    # Portfolio Performance
    plt.subplot(3, 1, 3)
    plt.title("Portfolio Performance")
    plt.plot(df.index, df["Portfolio_Value"], label="Portfolio Value", color='purple')
    plt.legend()
    
    plt.tight_layout()
    plt.show()

def analyze_strategy_performance(df, initial_capital=100000, realized_gains=None):
    """Comprehensive strategy performance analysis."""
    final_portfolio_value = df['Portfolio_Value'].iloc[-1]
    total_return = ((final_portfolio_value - initial_capital) / initial_capital) * 100
    
    print("\n--- Strategy Performance Report ---")
    print(f"Initial Capital: ₹{initial_capital:,.2f}")
    print(f"Final Portfolio Value: ₹{final_portfolio_value:,.2f}")
    print(f"Total Return: {total_return:.2f}%")
    
    if realized_gains:
        print(f"Number of Trades: {len(realized_gains)}")
        print(f"Total Realized Gains: ₹{sum(realized_gains):,.2f}")
        print(f"Average Trade Profit: ₹{np.mean(realized_gains):,.2f}")

def main(symbol="TCS.NS", initial_capital=100000):
    """Main strategy execution."""
    df = fetch_data(symbol)
    
    if df is not None:
        # Calculate advanced indicators
        df = calculate_advanced_indicators(df)
        
        # Backtest with adaptive strategy
        df, realized_gains = backtest_with_adaptive_strategy(df, initial_capital)
        
        # Visualize performance
        plot_comprehensive_performance(df, symbol)
        
        # Analyze performance
        analyze_strategy_performance(df, initial_capital, realized_gains)

# Execute strategy
if __name__ == "__main__":
    main()