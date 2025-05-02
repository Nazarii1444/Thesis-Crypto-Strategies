from typing import List

import plotly.graph_objects as go

from utils.indicators import add_ma
from utils.add_trades_marks import add_trades_marks
from utils.config import LONG, SHORT
from utils.utils import load_csv
from utils.stats import Stats
from utils.trade import Trade


def simulate_ma_14_ma_40_strategy(data):
    trades: List[Trade] = []
    position = None
    trade_id = 1
    cash, initial_cash = 1000, 1000
    lot_percentage = 0.12

    fast_period = 14
    slow_period = 40

    data = add_ma(data, fast_period)
    data = add_ma(data, slow_period)

    for i in range(slow_period, len(df)):
        date = data.index[i]
        current_close = data['Close'].iloc[i]

        prev_fast = data['MA_14'].iloc[i - 1]
        cur_fast = data['MA_14'].iloc[i]

        prev_slow = data['MA_40'].iloc[i - 1]
        cur_slow = data['MA_40'].iloc[i]

        up_cross = prev_slow > prev_fast and cur_fast > cur_slow
        down_cross = prev_fast > prev_slow and cur_fast < cur_slow

        if position is None:
            if up_cross:
                # Відкриття LONG позиції
                amount_in_dollars = cash * lot_percentage / 100
                trades.append(Trade(trade_id, LONG, amount_in_dollars, current_close, date))
                cash -= amount_in_dollars
                position = LONG
                trade_id += 1

            elif down_cross:
                # Відкриття SHORT позиції
                amount_in_dollars = cash * lot_percentage / 100
                trades.append(Trade(trade_id, SHORT, amount_in_dollars, current_close, date))
                cash -= amount_in_dollars
                position = SHORT
                trade_id += 1

        elif position == LONG:
            if down_cross:
                # Закриття LONG позиції
                trade = trades[-1]
                trade.close(current_close, date, cash)
                cash = trade.portfolio_value_after
                print(trade)

                # Відкриття SHORT позиції
                amount_in_dollars = cash * lot_percentage / 100
                short_position = Trade(trade_id, SHORT, amount_in_dollars, current_close, date)
                trades.append(short_position)
                cash -= amount_in_dollars
                position = SHORT
                trade_id += 1

        elif position == SHORT:
            if up_cross:
                # Закриття SHORT позиції
                trade = trades[-1]
                trade.close(current_close, date, cash)
                cash = trade.portfolio_value_after
                print(trade)

                # Відкриття LONG позиції
                amount_in_dollars = cash * lot_percentage / 100
                long_position = Trade(trade_id, LONG, amount_in_dollars, current_close, date)
                trades.append(long_position)
                cash -= amount_in_dollars
                position = LONG
                trade_id += 1

    Stats(initial_cash, lot_percentage, trades).export_stats_to_excel()
    plot_trades(data, trades)


def plot_trades(data, trades):
    fig = go.Figure()

    fig.add_trace(go.Scatter(x=data.index, y=data['Close'], mode='lines', name='Close'))

    fig.add_trace(go.Scatter(x=data.index, y=data['MA_14'], mode='lines', name='MA 14', line=dict(color='blue')))
    fig.add_trace(go.Scatter(x=data.index, y=data['MA_40'], mode='lines', name='MA 40', line=dict(color='orange')))

    fig = add_trades_marks(trades, fig)

    fig.update_layout(title="Стратегія MA 14 and MA 40",
                      xaxis_title="Дата",
                      yaxis_title="Ціна",
                      legend_title="Легенда",
                      xaxis_rangeslider_visible=False)

    fig.show()


if __name__ == '__main__':
    df = load_csv("../test_data/custom_csvs/AAVE_USDT_RECENT.csv")
    simulate_ma_14_ma_40_strategy(df)
