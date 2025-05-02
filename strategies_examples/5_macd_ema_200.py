from typing import List

import plotly.graph_objects as go
from plotly.subplots import make_subplots

from utils.indicators import add_ema, add_macd
from utils.add_trades_marks import add_trades_marks_
from utils.config import LONG, SHORT
from utils.utils import load_csv
from utils.stats import Stats
from utils.trade import Trade


def simulate_macd_ema200_strategy(data):
    trades: List[Trade] = []
    position = None
    trade_id = 1
    cash, initial_cash = 1000, 1000
    lot_percentage = 0.12

    ema_period = 200
    fast_period = 12
    slow_period = 26
    signal_period = 9

    data = add_ema(data, period=ema_period)
    data = add_macd(data, fast_period, slow_period, signal_period)

    for i in range(max(ema_period, slow_period), len(data)):
        date = data.index[i]
        current_close = data['Close'].iloc[i]
        ema_value = data[f'EMA_{ema_period}'].iloc[i]
        current_macd = data['MACD'].iloc[i]
        current_signal = data['MACD_Signal'].iloc[i]

        previous_macd = data['MACD'].iloc[i - 1]
        previous_signal = data['MACD_Signal'].iloc[i - 1]

        if position is None:
            if previous_macd < previous_signal and current_macd > current_signal and current_close > ema_value:
                # LONG
                amount_in_dollars = cash * lot_percentage / 100
                trades.append(Trade(trade_id, LONG, amount_in_dollars, current_close, date))
                cash -= amount_in_dollars
                position = LONG
                trade_id += 1

            elif previous_macd > previous_signal and current_macd < current_signal and current_close < ema_value:
                # SHORT
                amount_in_dollars = cash * lot_percentage / 100
                trades.append(Trade(trade_id, SHORT, amount_in_dollars, current_close, date))
                cash -= amount_in_dollars
                position = SHORT
                trade_id += 1

        elif position == LONG:
            if previous_macd > previous_signal and current_macd < current_signal and current_close < ema_value:
                # Закрити LONG, відкрити SHORT
                trade = trades[-1]
                trade.close(current_close, date, cash)
                cash = trade.portfolio_value_after
                print(trade)

                amount_in_dollars = cash * lot_percentage / 100
                trades.append(Trade(trade_id, SHORT, amount_in_dollars, current_close, date))
                cash -= amount_in_dollars
                position = SHORT
                trade_id += 1

        elif position == SHORT:
            if previous_macd < previous_signal and current_macd > current_signal and current_close > ema_value:
                # Закрити SHORT, відкрити LONG
                trade = trades[-1]
                trade.close(current_close, date, cash)
                cash = trade.portfolio_value_after
                print(trade)

                amount_in_dollars = cash * lot_percentage / 100
                trades.append(Trade(trade_id, LONG, amount_in_dollars, current_close, date))
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

    fig.add_trace(
        go.Scatter(
            x=data.index,
            y=data[f'EMA_{200}'],
            mode='lines',
            name='EMA 200',
            line=dict(color='orange', width=2)
        ),
        row=1, col=1
    )

    fig = add_trades_marks_(trades, fig, row=1, col=1)

    fig.add_trace(
        go.Bar(
            x=data.index,
            y=data['MACD_Hist'],
            name='MACD Histogram',
            marker_color=['green' if val >= 0 else 'red' for val in data['MACD_Hist']],
        ),
        row=2, col=1
    )

    fig.add_trace(
        go.Scatter(
            x=data.index,
            y=data['MACD'],
            mode='lines',
            name='MACD',
            line=dict(color='blue')
        ),
        row=2, col=1
    )

    fig.add_trace(
        go.Scatter(
            x=data.index,
            y=data['MACD_Signal'],
            mode='lines',
            name='MACD Signal',
            line=dict(color='red')
        ),
        row=2, col=1
    )

    fig.update_layout(
        title="Стратегія MACD crossover + EMA200 підтвердження",
        legend_title="Легенда",
        xaxis_rangeslider_visible=False
    )

    fig.update_xaxes(title_text="Дата", row=2, col=1)
    fig.update_yaxes(title_text="Ціна", row=1, col=1)
    fig.update_yaxes(title_text="MACD", row=2, col=1)

    fig.show()


if __name__ == '__main__':
    df = load_csv("../custom_test_data/custom_csvs/AAVE_USDT_RECENT.csv")
    simulate_macd_ema200_strategy(df)
