# ============================================================
# dashboard.py
# Creates a Streamlit dashboard for multi-asset portfolio analysis
# How to run it: streamlit run dashboard.py
# Requirements: streamlit, quantstats, pandas, matplotlib
# This dashboard allows users to input multiple stocks, their investment amounts, and a benchmark ticker.
# It then calculates portfolio performance metrics, displays an equity curve, and generates a full HTML report
# Limitations: it can be slow to download data for too many stocks so it is limited to 10, and the HTML report generation may take a few seconds.
# ============================================================


# setting up the page
import streamlit as st
import quantstats as qs
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import tempfile
st.set_page_config(
    page_title=" Portfolio Analysis for Multiple Assets",
    page_icon="📊",
    layout="wide"
)
st.title("📊 Portfolio Analysis for Multiple Assets")
st.markdown("""
This page demonstrates how to analyze a multi-asset portfolio using QuantStats.
We'll cover:
- Portfolio construction with custom weights""")
st.divider()

# creating where the user can input the details for the portfolio

st.sidebar.header("Portfolio details settings")
num_stocks = st.sidebar.number_input(
    "Enter the number of stocks you have in your portfolio", min_value=1, max_value=10, value=4, step=1)
st.sidebar.divider()
benchmark = st.sidebar.text_input("Benchmark", value="SPY")


# creating a loop to get the individual stock details from the user.
tickers = []
amounts = []
defaults = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 'JPM', 'V', 'UNH', 'HD', 'PG', 'DIS', 'MA', 'BAC',
            'VZ', 'ADBE', 'CMCSA', 'NFLX', 'INTC', 'PFE', 'KO', 'MRK', 'PEP', 'T', 'CSCO', 'XOM', 'CVX', 'WMT', 'BA', 'IBM']
for i in range(int(num_stocks)):

    value = defaults[i] if i < len(defaults) else ""
    st.sidebar.markdown(f"**Stock {i+1}**")
    col1, col2 = st.sidebar.columns([1, 1])

    with col1:
        ticker = st.text_input(f" Ticker symbol for stock {i+1}", value=value, key=f"ticker_{i}")
    with col2:
        amount = st.number_input(f"Amount invested in {ticker}",
                                 min_value=0.01, value=1000.0, step=100.0, key=f"amount_{i}")

    tickers.append(ticker)
    amounts.append(amount)

# Creating the run button to trigger the analysis and preview it.
total_investment_amount = sum(amounts)
st.sidebar.divider()
st.sidebar.markdown(f"**Your total investment amount: £{total_investment_amount:,.2f}**")
for t, a in zip(tickers, amounts):
    st.sidebar.write(f"{t}: £{a:,.2f} ({a/total_investment_amount:.2%})")
run = st.sidebar.button("Run Portfolio Analysis", use_container_width=True)

# Validating the input and running the analysis when the button is clicked.
if not run:
    st.info("Please enter your portfolio details and click 'Run Portfolio Analysis' to see the results.")
    st.stop()

if any(t == "" for t in tickers):
    st.error("Please ensure all ticker symbols are filled in.")
    st.stop()
if any(a <= 0 for a in amounts):
    st.error("Please ensure all investment amounts are positive.")
    st.stop()
if total_investment_amount <= 0:
    st.error("Total investment amount must be greater than 0.")
    st.stop()


# Downloading data to run the analysis.
weights_list = []
for a in amounts:
    # convertes the users amount into weights and storing them in a list called weights_list.
    weights_list.append(a / total_investment_amount)

progress_bar = st.progress(0)
status = st.empty()
all_returns = {}
for i, ticker in enumerate(tickers):
    status.text(f"Downloading return data for {ticker}...")
    try:
        returns = qs.utils.download_returns(ticker)
        all_returns[ticker] = returns
        progress_bar.progress((i + 1) / len(tickers))
    except Exception as e:
        st.error(f"Error downloading data for {ticker}: {e}")
        st.stop()
progress_bar.empty()
status.empty()
# data can contain empty cells so dropna() deletes or cleans the data to get consistent and accuarte results.
returns_df = pd.DataFrame(all_returns).dropna()
# multiplying each stock's return by its weight and summing them to get one blended return per day.
portfolio_returns = (returns_df * weights_list).sum(axis=1)
portfolio_returns.name = "Weighted Portfolio"

# benchmark returns
try:
    benchmark_returns = qs.utils.download_returns(benchmark)
except Exception as e:
    benchmark_returns = None

st.success("Data downloaded successfully! Running analysis...")

# portfolio composition display
st.subheader("Portfolio Composition")

cols = st.columns(len(tickers))
for col, ticker, amount, weight in zip(cols, tickers, amounts, weights_list):
    col.metric(
        label=ticker,
        value=f"£{amount:,.2f}",
        delta=f"{weight:.2%} of portfolio"
    )

st.divider()

# performance metrics display
st.subheader("Performance Metrics")
c1, c2, c3, c4 = st.columns(4)
c1.metric("annual return (CAGR)", f"{qs.stats.cagr(portfolio_returns):.2%}")
c2.metric("max drawdown", f"{qs.stats.max_drawdown(portfolio_returns):.2%}")
c3.metric("sharpe ratio", f"{qs.stats.sharpe(portfolio_returns):.2f}")
c4.metric("volatility", f"{qs.stats.volatility(portfolio_returns):.2%}")

c5, c6, c7, c8 = st.columns(4)
c5.metric("sortino ratio", f"{qs.stats.sortino(portfolio_returns):.2f}")
c6.metric("calmar ratio", f"{qs.stats.calmar(portfolio_returns):.2f}")
c7.metric("win rate", f"{qs.stats.win_rate(portfolio_returns):.2%}")
c8.metric("conditional value at risk", f"{qs.stats.cvar(portfolio_returns):.2%}")

st.divider()

# individual asset breakdown table
st.subheader("Individual Asset Performance")
asset_data = []
for ticker, weight in zip(tickers, weights_list):
    asset = all_returns[ticker].loc[portfolio_returns.index]
    asset_data.append({
        "Ticker": ticker,
        "Weight": f"{weight:.2%}",
        "CAGR": f"{qs.stats.cagr(asset):.2%}",
        "Sharpe": f"{qs.stats.sharpe(asset):.2f}",
        "Sortino": f"{qs.stats.sortino(asset):.2f}",
        "Max Drawdown": f"{qs.stats.max_drawdown(asset):.2%}",
        "Volatility": f"{qs.stats.volatility(asset):.2%}"
    })
st.dataframe(asset_data, use_container_width=True, hide_index=True)
st.divider()

# Equity curve chart
st.subheader("Equity Curve")
st.caption("Cumulative returns of the portfolio over time")
fig, ax = plt.subplots(figsize=(10, 6))
portfolio_cum_returns = (1 + portfolio_returns).cumprod() - 1
ax.plot(portfolio_cum_returns.index, portfolio_cum_returns.values, label="Portfolio", color="blue")
if benchmark_returns is not None:
    benchmark_cum_returns = (1 + benchmark_returns).cumprod() - 1
    ax.plot(benchmark_cum_returns.index, benchmark_cum_returns.values, label=benchmark, color="orange")
ax.set_title("Equity Curve — Cumulative Returns Over Time", fontsize=14)
ax.set_xlabel("Date", fontsize=12)
ax.set_ylabel("Cumulative Return", fontsize=12)
ax.legend()
ax.grid(True, alpha=0.3)
st.pyplot(fig)
plt.close(fig)
st.divider()

# correlation heatmap
st.subheader("Asset Correlation Matrix")
st.caption("Correlation coefficients between asset returns")
corr_matrix = returns_df.corr()
fig, ax = plt.subplots(figsize=(len(tickers) * 1.5, len(tickers) * 1.2))
im = ax.imshow(corr_matrix.values, cmap='RdYlGn', vmin=-1, vmax=1)
ax.set_xticks(range(len(tickers)))
ax.set_yticks(range(len(tickers)))
ax.set_xticklabels(tickers, fontsize=12)
ax.set_yticklabels(tickers, fontsize=12)
plt.colorbar(im, ax=ax, label='Correlation coefficient')
for i in range(len(tickers)):
    for j in range(len(tickers)):
        ax.text(j, i, f"{corr_matrix.iloc[i, j]:.3f}",
                ha="center", va="center", fontsize=11,
                fontweight="bold",
                # white text on dark squares so it is readable, black text on lighter squares
                color="white" if abs(corr_matrix.iloc[i, j]) > 0.7 else "black")
ax.set_title('Asset Correlation Matrix — Diversification Analysis', fontsize=14)
plt.tight_layout()
st.pyplot(fig)
plt.close(fig)
st.divider()

# generate full HTML report
st.subheader("Full HTML Report")
st.caption("Download a comprehensive report with detailed analytics and charts")
with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as tmp_file:
    report_path = tmp_file.name
bench = benchmark_returns if benchmark_returns is not None else benchmark
qs.reports.html(portfolio_returns, bench, output=report_path,
                title='Multi-Asset Portfolio Analysis')
with open(report_path, "r") as f:
    html_content = f.read()
st.download_button(
    label="Download Full HTML Report",
    data=html_content,
    file_name="multi_asset_portfolio_report.html",
    mime="text/html"
)
