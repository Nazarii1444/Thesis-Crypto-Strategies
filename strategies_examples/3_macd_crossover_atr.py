from typing import List

import plotly.graph_objects as go
from plotly.subplots import make_subplots

from utils.indicators import add_macd, add_atr
from utils.add_trades_marks import add_trades_marks_
from utils.config import LONG, SHORT
from utils.utils import load_csv
from utils.stats import Stats
from utils.trade import Trade


def simulate_macd_atr_strategy(data):
    trades: List[Trade] = []
    position = None
    trade_id = 1
    cash, initial_cash = 1000, 1000
    lot_percentage = 0.12

    fast_period = 12
    slow_period = 26
    signal_period = 9
    atr_period = 14

    data = add_macd(data, fast_period, slow_period, signal_period)
    data = add_atr(data, atr_period)

    take_profit_price = None
    stop_loss_price = None

    for i in range(max(slow_period, atr_period), len(data)):
        date = data.index[i]
        current_close = data['Close'].iloc[i]
        current_macd = data['MACD'].iloc[i]
        current_signal = data['MACD_Signal'].iloc[i]
        current_atr = data[f'ATR_{atr_period}'].iloc[i]

        previous_macd = data['MACD'].iloc[i - 1]
        previous_signal = data['MACD_Signal'].iloc[i - 1]

        if position is None:
            if previous_macd < previous_signal and current_macd > current_signal:
                # LONG signal
                amount_in_dollars = cash * lot_percentage / 100
                trades.append(Trade(trade_id, LONG, amount_in_dollars, current_close, date))
                cash -= amount_in_dollars
                position = LONG
                entry_price = current_close
                take_profit_price = entry_price + 2 * current_atr
                stop_loss_price = entry_price - 1 * current_atr
                trade_id += 1

            elif previous_macd > previous_signal and current_macd < current_signal:
                # SHORT signal
                amount_in_dollars = cash * lot_percentage / 100
                trades.append(Trade(trade_id, SHORT, amount_in_dollars, current_close, date))
                cash -= amount_in_dollars
                position = SHORT
                entry_price = current_close
                take_profit_price = entry_price - 2 * current_atr
                stop_loss_price = entry_price + 1 * current_atr
                trade_id += 1

        elif position == LONG:
            if current_close >= take_profit_price or current_close <= stop_loss_price:
                trade = trades[-1]
                trade.close(current_close, date, cash)
                cash = trade.portfolio_value_after
                print(trade)
                position = None

        elif position == SHORT:
            if current_close <= take_profit_price or current_close >= stop_loss_price:
                trade = trades[-1]
                trade.close(current_close, date, cash)
                cash = trade.portfolio_value_after
                print(trade)
                position = None

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
            line=dict(color='orange')
        ),
        row=2, col=1
    )

    fig.update_layout(
        title="MACD + ATR Take Profit/Stop Loss",
        legend_title="Легенда",
        xaxis_rangeslider_visible=False
    )

    fig.update_xaxes(title_text="Дата", row=2, col=1)
    fig.update_yaxes(title_text="Ціна", row=1, col=1)
    fig.update_yaxes(title_text="MACD", row=2, col=1)

    fig.show()


if __name__ == '__main__':
    df = load_csv("../custom_test_data/custom_csvs/AAVE_USDT_RECENT.csv")
    simulate_macd_atr_strategy(df)
