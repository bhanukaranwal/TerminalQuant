import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import requests
import pandas as pd
import json

# --- Configuration ---
API_URL = "http://backend:8000"

# --- Initialize Dash App ---
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server
app.title = "TerminalQuant"

# --- App Layout ---
app.layout = dbc.Container(
    fluid=True,
    className="bg-black text-light p-4",
    style={'font-family': "'IBM Plex Mono', monospace"},
    children=[
        dbc.Row(dbc.Col(html.H1("TerminalQuant 퀀", className="text-success text-center mb-4"))),
        dbc.Row([
            # Left Panel: Controls
            dbc.Col(dbc.Card([
                dbc.CardHeader("CONTROLS", className="text-warning"),
                dbc.CardBody([
                    html.H5("1. Select Optimization Model", className="card-title"),
                    dcc.Dropdown(
                        id='model-selector',
                        options=[
                            {'label': 'Mean-Variance Optimization (MVO)', 'value': 'mvo'},
                            {'label': 'Hierarchical Risk Parity (HRP)', 'value': 'hrp'},
                        ], value='mvo', clearable=False, className="mb-3"),
                    html.H5("2. Enter Asset Tickers", className="card-title mt-3"),
                    dbc.Input(id="input-tickers", placeholder="e.g., AAPL, GOOGL, MSFT", value="AAPL,MSFT,GOOGL,NVDA,TSLA,JPM,V", className="mb-3"),
                    html.Button("RUN OPTIMIZATION", id="run-opt-button", n_clicks=0, className="btn btn-primary w-100 mt-3"),
                ]),
            ]), md=3),
            # Right Panel: Outputs
            dbc.Col(dcc.Loading(id="loading-output", type="default", children=[html.Div(id='output-cards-container')]), md=9),
        ]),
    ]
)

# --- Callbacks ---
@app.callback(
    Output("output-cards-container", "children"),
    [Input("run-opt-button", "n_clicks")],
    [State("model-selector", "value"), State("input-tickers", "value")],
    prevent_initial_call=True
)
def run_full_workflow(n_clicks, selected_model, tickers_str):
    if not tickers_str:
        return dbc.Alert("Please enter at least one ticker.", color="warning")

    tickers_list = [ticker.strip().upper() for ticker in tickers_str.split(',')]
    
    try:
        # Step 1: Run Optimization
        opt_endpoint = "/optimize/mvo-tickers" if selected_model == 'mvo' else "/optimize/hrp"
        opt_response = requests.post(f"{API_URL}{opt_endpoint}", json={"tickers": tickers_list})
        opt_response.raise_for_status()
        opt_data = opt_response.json()
        if opt_data.get("status") != "success":
            return dbc.Alert(f"Optimization Error: {opt_data.get('message')}", color="danger")

        weights = opt_data.get("weights", {})
        
        # Step 2: Run Backtest
        backtest_payload = {"tickers": list(weights.keys()), "weights": weights}
        backtest_response = requests.post(f"{API_URL}/analysis/backtest", json=backtest_payload)
        backtest_response.raise_for_status()
        backtest_data = backtest_response.json()

        # Step 3: Get Efficient Frontier data (if MVO)
        ef_data = None
        if selected_model == 'mvo':
            ef_response = requests.post(f"{API_URL}/optimize/efficient-frontier", json={"tickers": tickers_list})
            ef_response.raise_for_status()
            ef_data = ef_response.json()

    except requests.exceptions.RequestException as e:
        return dbc.Alert(f"API Connection Error: {e}", color="danger")
    except json.JSONDecodeError:
        return dbc.Alert("Error decoding API response.", color="danger")

    # Step 4: Build UI components
    performance_card = build_performance_card(opt_data.get("performance", {}))
    allocation_card = build_allocation_card(weights)
    weights_card = build_weights_card(weights)
    backtest_card = build_backtest_card(backtest_data)
    frontier_card = build_frontier_card(ef_data) if selected_model == 'mvo' else None
    
    layout = []
    if backtest_card: layout.append(dbc.Row([dbc.Col(backtest_card, className="mb-4")]))
    if frontier_card: layout.append(dbc.Row([dbc.Col(frontier_card, className="mb-4")]))
    layout.append(dbc.Row([
        dbc.Col(performance_card, md=6, className="mb-4"),
        dbc.Col(allocation_card, md=6, className="mb-4"),
    ]))
    layout.append(dbc.Row([dbc.Col(weights_card, className="mb-4")]))

    return html.Div(layout)

# --- Helper functions to build cards ---
def build_performance_card(performance):
    return dbc.Card([
        dbc.CardHeader("PORTFOLIO PERFORMANCE", className="text-warning"),
        dbc.CardBody([
            html.H4(performance.get('expected_annual_return', 'N/A'), className="text-success"), html.P("Expected Annual Return", className="text-muted"),
            html.H4(performance.get('annual_volatility', 'N/A'), className="text-light"), html.P("Annual Volatility", className="text-muted"),
            html.H4(performance.get('sharpe_ratio', 'N/A'), className="text-warning"), html.P("Sharpe Ratio", className="text-muted"),
        ])
    ])

def build_allocation_card(weights):
    fig = {'data': [{'values': list(weights.values()), 'labels': list(weights.keys()), 'type': 'pie', 'hole': .4, 'marker': {'colors': ['#00ff00', '#ffff00', '#00ffff', '#ff00ff', '#ffffff', '#ff9900']}, 'textinfo': 'percent', 'hoverinfo': 'label+percent'}], 'layout': {'showlegend': False, 'paper_bgcolor': '#0d0d0d', 'font': {'color': '#d3d3d3'}, 'margin': {'t': 10, 'b': 10, 'l': 10, 'r': 10}}}
    return dbc.Card([dbc.CardHeader("OPTIMAL ASSET ALLOCATION", className="text-warning"), dbc.CardBody(dcc.Graph(figure=fig, style={'height': '310px'}))])

def build_weights_card(weights):
    df = pd.DataFrame(list(weights.items()), columns=['Asset', 'Weight'])
    df['Weight'] = df['Weight'].apply(lambda x: f"{x:.2%}")
    table = dash_table.DataTable(
        columns=[{"name": i, "id": i} for i in df.columns], data=df.to_dict('records'),
        style_cell={'textAlign': 'left', 'backgroundColor': '#0d0d0d', 'color': '#d3d3d3', 'border': '1px solid #333', 'fontFamily': "'IBM Plex Mono', monospace"},
        style_header={'backgroundColor': '#1a1a1a', 'fontWeight': 'bold', 'color': '#ffff00', 'fontFamily': "'IBM Plex Mono', monospace"},
        style_as_list_view=True)
    return dbc.Card([dbc.CardHeader("WEIGHTS", className="text-warning"), dbc.CardBody(table)])

def build_backtest_card(backtest_data):
    if not backtest_data or backtest_data.get("status") != "success": return None
    df = pd.DataFrame(backtest_data['data'])
    fig = {'data': [
        {'x': df['date'], 'y': df['portfolio'], 'mode': 'lines', 'name': 'Your Portfolio', 'line': {'color': '#00ff00'}},
        {'x': df['date'], 'y': df['benchmark'], 'mode': 'lines', 'name': backtest_data.get("benchmark_ticker", "Benchmark"), 'line': {'color': '#00ffff', 'dash': 'dash'}}
    ], 'layout': {'xaxis': {'gridcolor': '#333'}, 'yaxis': {'gridcolor': '#333', 'tickformat': '.1%'}, 'paper_bgcolor': '#0d0d0d', 'plot_bgcolor': '#0d0d0d', 'font': {'color': '#d3d3d3'}, 'legend': {'orientation': 'h', 'y': -0.2}}}
    return dbc.Card([dbc.CardHeader("PORTFOLIO BACKTEST", className="text-warning"), dbc.CardBody(dcc.Graph(figure=fig, style={'height': '400px'}))])

def build_frontier_card(ef_data):
    if not ef_data or ef_data.get("status") != "success": return None
    frontier = ef_data['frontier_points']
    max_sharpe = ef_data['max_sharpe_point']
    min_vol = ef_data['min_vol_point']
    fig = {'data': [
        {'x': frontier['risk'], 'y': frontier['return'], 'mode': 'lines', 'name': 'Efficient Frontier', 'line': {'color': '#00ffff'}},
        {'x': [max_sharpe['risk']], 'y': [max_sharpe['return']], 'mode': 'markers', 'name': 'Max Sharpe', 'marker': {'color': '#00ff00', 'size': 12, 'symbol': 'star'}},
        {'x': [min_vol['risk']], 'y': [min_vol['return']], 'mode': 'markers', 'name': 'Min Volatility', 'marker': {'color': '#ffff00', 'size': 12, 'symbol': 'diamond'}},
    ], 'layout': {'xaxis': {'title': 'Volatility (Risk)', 'gridcolor': '#333', 'tickformat': '.1%'}, 'yaxis': {'title': 'Expected Return', 'gridcolor': '#333', 'tickformat': '.1%'}, 'paper_bgcolor': '#0d0d0d', 'plot_bgcolor': '#0d0d0d', 'font': {'color': '#d3d3d3'}, 'legend': {'orientation': 'h', 'y': -0.2}}}
    return dbc.Card([dbc.CardHeader("EFFICIENT FRONTIER", className="text-warning"), dbc.CardBody(dcc.Graph(figure=fig, style={'height': '400px'}))])

if __name__ == "__main__":
    app.run_server(debug=True, host='0.0.0.0', port=8050)
