# ============================================================
#  run_original.py
#  A simple script to demonstrate QuantStats' core functionality
#  It downloads return data for Apple (AAPL), prints key metrics, and generates a full HTML report comparing AAPL to the S&P 500 (SPY).
#  To run: python3 run_original.py
#  Requirements: quantstats, pandas, numpy, matplotlib
# ============================================================

import quantstats as qs

# Download Apple stock return data from Yahoo Finance
# QuantStats uses yfinance under the hood to fetch real data
stock = qs.utils.download_returns('AAPL')

# Print key financial metrics to the terminal
print("=" * 45)
print("   QUANTSTATS — APPLE (AAPL) ANALYSIS")
print("=" * 45)
print(f"Sharpe Ratio:         {qs.stats.sharpe(stock):.2f}")
print(f"Sortino Ratio:        {qs.stats.sortino(stock):.2f}")
print(f"Max Drawdown:         {qs.stats.max_drawdown(stock):.2%}")
print(f"Annual Return (CAGR): {qs.stats.cagr(stock):.2%}")
print(f"Volatility:           {qs.stats.volatility(stock):.2%}")
print(f"Calmar Ratio:         {qs.stats.calmar(stock):.2f}")
print(f"Win Rate:             {qs.stats.win_rate(stock):.2%}")
print(f"Avg Win:              {qs.stats.avg_win(stock):.2%}")
print(f"Avg Loss:             {qs.stats.avg_loss(stock):.2%}")
print("=" * 45)

# Generate the full HTML tear sheet report
# This benchmarks AAPL against the S&P 500 (SPY)
print("\nGenerating full HTML tear sheet report...")
qs.reports.html(stock, 'SPY', output='aapl_report.html',
                title='Apple (AAPL) Portfolio Analysis')
print("Report saved as aapl_report.html — open in your browser")