import pandas as pd

# Parameters
SHORT_WINDOW = 20
LONG_WINDOW = 50
INITIAL_CAPITAL = 1000

# First, I loaded my previously saved stock data
# The CSV file should have at least a 'date' and 'close' column.
# If 'date' is present, parse it and set it as index.
df = pd.read_csv('daily_TSLA.csv', parse_dates=True)

# Ensure data is sorted by date
df = df.sort_values(by='timestamp', ascending=True).reset_index(drop=True)

# Calculate moving averages
df['MA_short'] = df['close'].rolling(window=SHORT_WINDOW).mean()
df['MA_long'] = df['close'].rolling(window=LONG_WINDOW).mean()

# Generate signals: 

df['signal'] = 0
for i in df.index:
    if df.at[i,'MA_short'] > df.at[i, 'MA_long']: df.loc[i, 'signal'] = 1
    else: df.loc[i, 'signal'] = 0


# Find trade signals by checking when our signal changes from 0 to 1 (buy) and 1 to 0 (sell)
df['advice'] = 'HOLD'
for i in range(1, len(df)):
   action = df.at[i, 'signal'] - df.at[i - 1, 'signal']
   if action < 0: 
       df.loc[i, 'advice'] = 'SELL' 
       print(f"SELL STOCK - stock price: {df.at[df.index[i], 'close']} date: {df.at[df.index[i], 'timestamp']}")
   elif action > 0: 
       df.loc[i, 'advice'] = 'BUY'
       print(f"BUY STOCK - stock price: {df.at[df.index[i], 'close']} date: {df.at[df.index[i], 'timestamp']}")
   else: df.loc[i, 'advice'] = 'HOLD'
       


# Backtesting the Strategy
# We'll assume we invest our entire capital when signal = 1 and go to cash when signal = 0.
# For simplicity, we assume we buy/sell at the 'close' price on the day the signal is generated.
capital = INITIAL_CAPITAL
position = 0  # number of shares we hold

# We’ll track portfolio value over time
portfolio_values = []

for i in df.index:
    row = df.iloc[i]
    price = row['close']
    pos_change = row['advice']  

    if pos_change == 'BUY':
       
        shares = capital / price
        position = shares
        capital = 0
    elif pos_change == 'SELL':
       
        capital = position * price
        position = 0
    
    # Current portfolio value: if we hold shares, value = shares * price; if cash, value = capital
    if position > 0:
        portfolio_value = position * price
    else:
        portfolio_value = capital
    
    portfolio_values.append(portfolio_value)

df['portfolio_value'] = portfolio_values

# Print final results
final_value = df['portfolio_value'].iloc[-1]
total_return = (final_value - INITIAL_CAPITAL) / INITIAL_CAPITAL * 100
print(f"Final portfolio value: ${final_value:.2f}")
print(f"Total Return: {total_return:.2f}%")

# Plot the results (optional, if you have matplotlib)
import matplotlib.pyplot as plt
plt.figure(figsize=(12, 6))
plt.plot(df.index, df['portfolio_value'], label='Strategy Portfolio Value')
plt.title("Strategy Backtest")
plt.xlabel("Date")
plt.ylabel("Portfolio Value ($)")
plt.legend()
plt.show()
plt.savefig('trading_graph')