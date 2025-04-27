from typing import List

import plotly.graph_objects as go
from plotly.subplots import make_subplots

from indicators import add_rsi
from utils.add_trades_marks import add_trades_marks_
from utils.config import LONG, SHORT
from utils.loader import load_csv
from utils.stats import Stats
from utils.trade import Trade


def simulate_rsi_strategy(data):
    trades: List[Trade] = []
    position = None
    trade_id = 1
    cash, initial_cash = 1000, 1000
    lot_percentage = 0.12
    period = 14

    lower_bound = 30
    upper_bound = 70
    data = add_rsi(data, period=period)

    for i in range(period, len(data)):
        date = data.index[i]
        current_close = data['Close'].iloc[i]
        current_rsi = data['RSI'].iloc[i]

        if position is None:
            if current_rsi < lower_bound:
                amount_in_dollars = cash * lot_percentage / 100
                trades.append(Trade(trade_id, LONG, amount_in_dollars, current_close, date))
                cash -= amount_in_dollars
                position = LONG
                trade_id += 1

            elif current_rsi > upper_bound:
                amount_in_dollars = cash * lot_percentage / 100
                trades.append(Trade(trade_id, SHORT, amount_in_dollars, current_close, date))
                cash -= amount_in_dollars
                position = SHORT
                trade_id += 1

        elif position == LONG:
            if current_rsi > upper_bound:
                trade = trades[-1]
                trade.close(current_close, date, cash)
                cash = trade.portfolio_value_after
                print(trade)

                amount_in_dollars = cash * lot_percentage / 100
                short_position = Trade(trade_id, SHORT, amount_in_dollars, current_close, date)
                trades.append(short_position)
                cash -= amount_in_dollars
                position = SHORT
                trade_id += 1

        elif position == SHORT:
            if current_rsi < lower_bound:
                trade = trades[-1]
                trade.close(current_close, date, cash)
                cash = trade.portfolio_value_after
                print(trade)

                amount_in_dollars = cash * lot_percentage / 100
                long_position = Trade(trade_id, LONG, amount_in_dollars, current_close, date)
                trades.append(long_position)
                cash -= amount_in_dollars
                position = LONG
                trade_id += 1

    Stats(initial_cash, lot_percentage, trades).export_stats_to_excel()
    plot_trades(data, trades)


def plot_trades(data, trades):
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.02,
        row_heights=[0.7, 0.3]
    )

    fig.add_trace(
        go.Scatter(
            x=data.index,
            y=data['Close'],
            mode='lines',
            name='Close Price'
        ),
        row=1, col=1
    )

    fig = add_trades_marks_(trades, fig, row=1, col=1)

    fig.add_trace(
        go.Scatter(
            x=data.index,
            y=data['RSI'],
            mode='lines',
            name='RSI',
            line=dict(color='purple')
        ),
        row=2, col=1
    )

    fig.add_hline(
        y=30,
        line_dash='dash',
        line_color='gray',
        row=2, col=1
    )
    fig.add_hline(
        y=70,
        line_dash='dash',
        line_color='gray',
        row=2, col=1
    )

    fig.update_layout(
        title="Стратегія RSI (< 30 / > 70)",
        legend_title="Легенда",
        xaxis_rangeslider_visible=False
    )

    fig.update_xaxes(title_text="Дата", row=2, col=1)
    fig.update_yaxes(title_text="Ціна", row=1, col=1)
    fig.update_yaxes(title_text="RSI", row=2, col=1)

    fig.show()


if __name__ == '__main__':
    df = load_csv("../test_data/custom_csvs/AAVE_USDT_RECENT.csv")
    simulate_rsi_strategy(df)
