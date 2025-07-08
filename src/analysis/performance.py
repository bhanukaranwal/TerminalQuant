import pandas as pd
import yfinance as yf
from typing import Dict

def calculate_backtest(
    prices: pd.DataFrame,
    weights: Dict[str, float],
    benchmark_ticker: str = 'SPY'
) -> Dict:
    """
    Calculates the cumulative historical performance of a portfolio and a benchmark.
    """
    try:
        portfolio_weights = pd.Series(weights, index=prices.columns).fillna(0)
        daily_returns = prices.pct_change().dropna()
        portfolio_returns = (daily_returns * portfolio_weights).sum(axis=1)
        cumulative_portfolio_returns = (1 + portfolio_returns).cumprod() - 1

        benchmark_data = yf.download(benchmark_ticker, start=prices.index.min(), end=prices.index.max())['Adj Close']
        benchmark_returns = benchmark_data.pct_change().dropna()
        cumulative_benchmark_returns = (1 + benchmark_returns).cumprod() - 1

        result_df = pd.DataFrame({
            'date': cumulative_portfolio_returns.index.strftime('%Y-%m-%d'),
            'portfolio': cumulative_portfolio_returns.values,
        }).merge(
            pd.DataFrame({
                'date': cumulative_benchmark_returns.index.strftime('%Y-%m-%d'),
                'benchmark': cumulative_benchmark_returns.values
            }),
            on='date',
            how='inner'
        )

        return {
            "status": "success",
            "data": result_df.to_dict('records'),
            "benchmark_ticker": benchmark_ticker
        }
    except Exception as e:
        return {"status": "error", "message": f"An error occurred during backtesting: {str(e)}"}
