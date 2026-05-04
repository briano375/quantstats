

# ============================================================
# multi_portfolio.py
# This script allows users to analyze a multi-asset portfolio with custom weights using QuantStats.
# It prompts the user for the number of stocks, their tickers, investment amounts, and a benchmark ticker.
# The script then calculates performance metrics for the blended portfolio, generates a correlation matrix, and creates a full HTML report.
# To run: python3 multi_portfolio.py
# Requirements: quantstats, pandas, numpy, matplotlib
# ============================================================
# imports
import quantstats as qs
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt 


# welcome message
print("============================================================")
print("MULTI-ASSET WEIGHTED PORTFOLIO BUILDER")
print("This is a financial improvement component that allows users to analyze a portfolio of multiple stocks with custom weights.")
print("============================================================")


# Get Number of stocks in the portfolio from user input
while True:
    try:
        num_stocks = int(input("Enter the number of stocks in your portfolio: "))
        if num_stocks <= 0:
            print("Please enter a positive integer.")
            continue
        break
    except ValueError:
        print("Invalid input. Please enter a valid integer.")

#  Get the bechmark ticker from user input
benchmark = input("Enter the benchmark ticker (e.g., SPY): ").upper()
#   Validate benchmark input by attempting to download data
try:
   benchmark_data = qs.utils.download_returns(benchmark)
except Exception as e:
    print(f"Error downloading data for benchmark {benchmark}: {e}")
    exit()
    
# Get stock tickers and amounts invested from user input
portfolio = {}
total_value = 0 
for i in range(num_stocks):
    ticker = input(f"Enter the ticker symbol for stock {i+1}: ").upper()
    while True:
        try:
            amount = float(input(f"Enter the amount invested in {ticker}: "))
            if amount <= 0:
                print("Please enter a positive number.")
                continue
            break
        except ValueError:
            print("Invalid input. Please enter a valid number.")
    portfolio[ticker] = amount
    total_value += amount

# Calculate weights for each stock
if total_value == 0:
    print("Total investment amount cannot be zero.")
    exit()
weights = {ticker: amount / total_value for ticker, amount in portfolio.items()}  # converting the  user's amount in to weights by using the total amount to divide a single stock amount.

# display portfolio composition 
print("\nYour Portfolio Composition:")
for ticker, amount in portfolio.items():
    bar_length = int(weights[ticker] * 50)
    print(f"{ticker}: £{amount:,.2f} ({weights[ticker]:.2%})[{'#' * bar_length}{' ' * (50 - bar_length)}]")
  
print(f"\nTotal invested: £{total_value:,.2f}")


# Downloading data to run the analysis.
print("\nDownloading return data for your portfolio...")
all_returns = {}
for ticker in portfolio.keys():
    try:
        print(f"  Fetching {ticker}...", end=" ")
        returns = qs.utils.download_returns(ticker)
        all_returns[ticker] = returns
        print("done")   
    except Exception as e:
        print(f"Error downloading data for {ticker}: {e}")
        exit()
returns_df = pd.DataFrame(all_returns).dropna()  # this downloads data and also cleans it by deleting empty cells and presenting the accurate data.

# build blended portfolio returns series
weights_list = [weights[ticker] for ticker in portfolio.keys()]
portfolio_returns = (returns_df * weights_list).sum(axis=1) # this multiplies each stock's return by its weight and sums them to get one combined return per day.
print(f"\nData aligned: {len(returns_df)} trading days")
print(f"Date range: {returns_df.index[0].date()} to {returns_df.index[-1].date()}")
portfolio_returns.name = "Weighted Portfolio"

# correlation matrix
print("\nCalculating correlation matrix...")
correlation_matrix = returns_df.corr()
print("\nCorrelation Matrix:")
print(correlation_matrix)   
plt.figure(figsize=(8, 6))
plt.imshow(correlation_matrix, cmap='coolwarm', vmin=-1, vmax=1)
plt.colorbar(label='Correlation Coefficient')
plt.xticks(ticks=range(len(correlation_matrix)), labels=correlation_matrix.columns, rotation=45)
plt.yticks(ticks=range(len(correlation_matrix)), labels=correlation_matrix.columns)
plt.title('Correlation Matrix of Stock Returns')
plt.tight_layout()
for i in range(len(correlation_matrix)):
    for j in range(len(correlation_matrix)):
        plt.text(j, i, f"{correlation_matrix.iloc[i, j]:.2f}", ha='center', va='center', color='black')
plt.savefig('correlation_matrix.png')
plt.close()
print("Correlation matrix saved as correlation_matrix.png")

# Individual asset metrics table
print("\nCalculating performance metrics for each stock...")
metrics_table = pd.DataFrame(index=returns_df.columns)
metrics_table['weight'] = [f"{weights[ticker]:.2%}" for ticker in returns_df.columns if ticker in weights]
metrics_table['Sharpe Ratio'] = returns_df.apply(qs.stats.sharpe)
metrics_table['Sortino Ratio'] = returns_df.apply(qs.stats.sortino)
metrics_table['Max Drawdown'] = returns_df.apply(qs.stats.max_drawdown)
metrics_table['Annual Return (CAGR)'] = returns_df.apply(qs.stats.cagr)
metrics_table['Volatility'] = returns_df.apply(qs.stats.volatility)
print("\nIndividual Asset Performance Metrics:")
print(metrics_table.to_string(float_format="{:.2f}".format))    


# Blended portfolio metrics
print("\nCalculating performance metrics for the multi_portfolio...")
print("=" * 45)
print("  MULTI-PORTFOLIO METRICS")
print("=" * 45)

portfolio_metrics = {
    "Sharpe Ratio": qs.stats.sharpe(portfolio_returns),
    "Sortino Ratio": qs.stats.sortino(portfolio_returns),
    "Max Drawdown": qs.stats.max_drawdown(portfolio_returns),
    "Annual Return (CAGR)": qs.stats.cagr(portfolio_returns),
    "Volatility": qs.stats.volatility(portfolio_returns),
    "Calmar Ratio": qs.stats.calmar(portfolio_returns),
    "Win Rate": qs.stats.win_rate(portfolio_returns),
    "CVaR (99%)": qs.stats.cvar(portfolio_returns),
}
pct_metrics = ["Drawdown", "Return", "Volatility", "Rate", "CVaR"] #this helps to identify the matrics to format.
for metric, value in portfolio_metrics.items():
    if any(word in metric for word in pct_metrics):
        print(f"{metric}: {value:.2%}")
    else:
        print(f"{metric}: {value:.2f}")

# Generate HTML report
print("\nGenerating full HTML tear sheet report for the multi_portfolio...")
qs.reports.html(portfolio_returns, benchmark, output='multi_portfolio_report.html',
                title='Multi-Portfolio Analysis')
print("Report saved as multi_portfolio_report.html — open in your browser")
print("\n" + "=" * 45)
print("  ANALYSIS COMPLETE")
print("=" * 45)
print(f"Portfolio analysed: {', '.join(portfolio.keys())}")
print(f"Total invested: £{total_value:,.2f}")
print("Open multi_portfolio_report.html in your browser for the full report.")
