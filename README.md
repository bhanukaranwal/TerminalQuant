# TerminalQuant 퀀

**TerminalQuant** is an open-source Portfolio Optimization Tool inspired by the sleek, data-rich aesthetic of the Bloomberg Terminal. It enables users to build, optimize, analyze, and backtest investment portfolios with advanced financial models and interactive visualizations.

## Key Features

- **Advanced Optimization:** Choose between Mean-Variance Optimization (MVO) and Hierarchical Risk Parity (HRP).
- **Interactive Dashboard:** A dark-themed, modular UI built with Dash.
- **Rich Visualizations:** Efficient Frontier, dynamic asset allocation pie charts, and historical performance backtesting against the S&P 500 benchmark.
- **Flexible Data Sources:** Fetches data automatically from Yahoo Finance (`yfinance`).

## Getting Started (with Docker)

This is the recommended way to run the application.

### Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/)

### Installation & Running

1.  **Clone the repository:**
    ```sh
    git clone [https://github.com/your-username/TerminalQuant.git](https://github.com/your-username/TerminalQuant.git)
    cd TerminalQuant
    ```

2.  **Build and run the application:**
    ```sh
    docker-compose up --build
    ```

3.  **Access the application:**
    Open your web browser and navigate to **`http://localhost:8050`**.

## Contributing

Contributions are welcome! Please read `CONTRIBUTING.md` for details on how to get started.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.
