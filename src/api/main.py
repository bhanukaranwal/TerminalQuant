from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict
from datetime import date

from src.data.data_fetcher import fetch_daily_prices
from src.optimization.optimizers import calculate_mvo, calculate_efficient_frontier, calculate_hrp
from src.analysis.performance import calculate_backtest

app = FastAPI(
    title="TerminalQuant API",
    description="An API for advanced portfolio optimization and analysis.",
    version="1.0.0"
)

# --- Pydantic Models ---
class TickerInput(BaseModel):
    tickers: List[str]
    start_date: date = date(date.today().year - 5, date.today().month, date.today().day)
    end_date: date = date.today()

class BacktestInput(BaseModel):
    tickers: List[str]
    weights: Dict[str, float]
    start_date: date = date(date.today().year - 5, date.today().month, date.today().day)
    end_date: date = date.today()

# --- Endpoints ---
@app.post("/optimize/mvo-tickers")
def optimize_portfolio_from_tickers(input_data: TickerInput):
    prices = fetch_daily_prices(input_data.tickers, str(input_data.start_date), str(input_data.end_date))
    if prices.empty:
        raise HTTPException(status_code=400, detail="Could not fetch price data.")
    result = calculate_mvo(prices)
    if result["status"] == "error":
        raise HTTPException(status_code=500, detail=result["message"])
    return result

@app.post("/optimize/hrp")
def optimize_portfolio_hrp(input_data: TickerInput):
    prices = fetch_daily_prices(input_data.tickers, str(input_data.start_date), str(input_data.end_date))
    if prices.empty:
        raise HTTPException(status_code=400, detail="Could not fetch price data.")
    result = calculate_hrp(prices)
    if result["status"] == "error":
        raise HTTPException(status_code=500, detail=result["message"])
    return result

@app.post("/optimize/efficient-frontier")
def get_efficient_frontier(input_data: TickerInput):
    prices = fetch_daily_prices(input_data.tickers, str(input_data.start_date), str(input_data.end_date))
    if prices.empty:
        raise HTTPException(status_code=400, detail="Could not fetch price data.")
    result = calculate_efficient_frontier(prices)
    if result["status"] == "error":
        raise HTTPException(status_code=500, detail=result["message"])
    return result

@app.post("/analysis/backtest")
def get_backtest_performance(input_data: BacktestInput):
    prices = fetch_daily_prices(input_data.tickers, str(input_data.start_date), str(input_data.end_date))
    if prices.empty:
        raise HTTPException(status_code=400, detail="Could not fetch price data for backtesting.")
    result = calculate_backtest(prices, input_data.weights)
    if result["status"] == "error":
        raise HTTPException(status_code=500, detail=result["message"])
    return result
