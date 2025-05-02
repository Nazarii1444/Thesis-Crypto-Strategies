import random
from typing import List

import plotly.graph_objects as go

from utils.additional_position import AdditionalPosition
from utils.config import LONG, SHORT
from utils.stats import Stats
from utils.utils import load_csv


def has_to_be_closed(position, current_close, trade):
    return (
            (position == LONG and current_close >= trade.expected_price_to_exit) or
            (position == SHORT and current_close <= trade.expected_price_to_exit)
    )


def test_strategy(filepath):
    data = load_csv(filepath)

    trades: List[AdditionalPosition] = []
    position = None
    trade_id = 1
    cash, initial_cash = 100, 100
    lot_percentage = 5
    current_invest_value = lot_percentage * 100 / cash

    for i in range(2, len(data)):
        current_close = data['Close'].iloc[i]
        date = data.index[i]

        if position is None:
            if current_invest_value <= 0:
                print(f"Insufficient funds to open a new position: {cash}")
                break

            # Відкриття довгої або короткої позиції РАНДОМНО
            side = random.choice([LONG, SHORT])
            current_invest_value = cash * lot_percentage / 100
            trades.append(AdditionalPosition(trade_id, side, current_invest_value, current_close, date))
            cash -= current_invest_value
            position = side
            trade_id += 1
        elif position is not None:
            trade = trades[-1]

            if has_to_be_closed(position, current_close, trade):
                trade.close(current_close, date, cash)
                cash = trade.portfolio_value_after
                print(f"{trade}\n")
                position = None
            else:
                if trade.should_create_additional_purchase(current_close):
                    to_add = current_invest_value

                    # if trade.times_made_additional_purchase >= 1:
                    #     if cash >= to_add * 1:
                    #         to_add *= 1

                    trade.create_additional_purchase(current_close, to_add, date)
                    cash -= to_add

    Stats(initial_cash, lot_percentage, trades).export_stats_to_excel()
    plot_trades(data, trades)


def plot_trades(data, trades):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data.index, y=data['Close'], mode='lines', name='Close'))

    for trade in trades:
        if trade.closed:
            fig.add_trace(go.Scatter(
                x=[trade.open_datetime], y=[trade.open_price],
                mode='markers',
                marker=dict(color='green' if trade.profit > 0 else 'red', size=12),
                name=f'Trade {trade.trade_id} Start'
            ))
            fig.add_trace(go.Scatter(
                x=[trade.close_datetime], y=[trade.close_price],
                mode='markers',
                marker=dict(color='green' if trade.profit > 0 else 'red', size=12),
                name=f'Trade {trade.trade_id} End'
            ))
            fig.add_trace(go.Scatter(
                x=[trade.open_datetime, trade.close_datetime], y=[trade.open_price, trade.close_price],
                mode='lines',
                line=dict(color='purple', dash='dash'),
                name=f'Trade {trade.trade_id} Line'
            ))

            for purchase in trade.additional_purchases[1:]:
                fig.add_trace(go.Scatter(
                    x=[purchase.date], y=[purchase.open_price],
                    mode='markers',
                    marker=dict(color='blue', size=8, symbol='triangle-down'),
                    name=f'Additional Purchase Trade {trade.trade_id}'
                ))

    fig.update_layout(
        legend_title="Legend",
        xaxis_rangeslider_visible=False,
        margin=dict(l=0, r=0, t=16, b=0),
        paper_bgcolor='white',
    )
    fig.show()


if __name__ == '__main__':
    filepath = '../custom_test_data/custom_csvs/AAVE_USDT_RECENT.csv'
    test_strategy(filepath)
