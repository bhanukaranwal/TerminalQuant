import pandas as pd
from pypfopt import EfficientFrontier, risk_models, expected_returns, plotting
from pypfopt.hierarchical_portfolio import HRPOpt

def calculate_mvo(prices: pd.DataFrame, risk_free_rate: float = 0.02):
    try:
        mu = expected_returns.mean_historical_return(prices)
        S = risk_models.sample_cov(prices)
        ef = EfficientFrontier(mu, S)
        weights = ef.max_sharpe(risk_free_rate=risk_free_rate)
        cleaned_weights = dict(ef.clean_weights())
        performance = ef.portfolio_performance(verbose=False, risk_free_rate=risk_free_rate)
        formatted_performance = {
            "expected_annual_return": f"{performance[0]:.2%}",
            "annual_volatility": f"{performance[1]:.2%}",
            "sharpe_ratio": f"{performance[2]:.2f}"
        }
        return {"status": "success", "weights": cleaned_weights, "performance": formatted_performance}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def calculate_hrp(prices: pd.DataFrame):
    try:
        returns = expected_returns.returns_from_prices(prices)
        hrp = HRPOpt(returns)
        weights = hrp.optimize()
        cleaned_weights = dict(hrp.clean_weights())
        performance = hrp.portfolio_performance(verbose=False)
        formatted_performance = {
            "expected_annual_return": f"{performance[0]:.2%}",
            "annual_volatility": f"{performance[1]:.2%}",
            "sharpe_ratio": f"{performance[2]:.2f}"
        }
        return {"status": "success", "weights": cleaned_weights, "performance": formatted_performance}
    except Exception as e:
        return {"status": "error", "message": f"An unexpected error occurred during HRP: {str(e)}"}

def calculate_efficient_frontier(prices: pd.DataFrame, risk_free_rate: float = 0.02):
    try:
        mu = expected_returns.mean_historical_return(prices)
        S = risk_models.sample_cov(prices)
        ef = EfficientFrontier(mu, S)
        
        ef_max_sharpe = ef.deepcopy()
        ef_max_sharpe.max_sharpe(risk_free_rate=risk_free_rate)
        max_sharpe_perf = ef_max_sharpe.portfolio_performance(verbose=False, risk_free_rate=risk_free_rate)
        max_sharpe_point = {"risk": max_sharpe_perf[1], "return": max_sharpe_perf[0]}

        ef_min_vol = ef.deepcopy()
        ef_min_vol.min_volatility()
        min_vol_perf = ef_min_vol.portfolio_performance(verbose=False, risk_free_rate=risk_free_rate)
        min_vol_point = {"risk": min_vol_perf[1], "return": min_vol_perf[0]}
        
        ef_frontier = ef.deepcopy()
        frontier_risk, frontier_return, _ = plotting.plot_efficient_frontier(ef_frontier, showfig=False, num_points=100)
        
        return {
            "status": "success",
            "frontier_points": {"risk": frontier_risk.tolist(), "return": frontier_return.tolist()},
            "max_sharpe_point": max_sharpe_point,
            "min_vol_point": min_vol_point
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
