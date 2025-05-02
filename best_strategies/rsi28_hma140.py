from typing import List

from utils.additional_position import AdditionalPosition
from utils.config import LONG
from utils.indicators import add_hma, add_rsi
import pandas as pd
import plotly.graph_objects as go

from utils.stats import Stats
from utils.utils import load_csv


RSI_PERIOD = 18
HMA_PERIOD = 25

def end_of_negative_slope(prev_slope, cur_slope):
    return prev_slope < 0 < cur_slope


def end_of_positive_slope(prev_slope, cur_slope):
    return prev_slope > 0 > cur_slope


def test_strategy(filepath):
    df = load_csv(filepath)

    position = None
    trades: List[AdditionalPosition] = []
    trade_id = 1
    cash, initial_cash = 1000, 1000
    lot_percentage = 0.12
    current_invest_value = cash * lot_percentage

    df = add_rsi(df, RSI_PERIOD)
    df = add_hma(df, HMA_PERIOD)
    df['SLOPE'] = df[f'HMA_{HMA_PERIOD}'].diff()

    for i in range(HMA_PERIOD, len(df)):
        row = df.iloc[i]
        prev_row = df.iloc[i - 1]
        date = row.name

        current_price = row['Close']
        rsi = row[f'RSI_{RSI_PERIOD}']
        cur_slope = row['SLOPE']
        prev_slope = prev_row['SLOPE']

        if position is None:
            if rsi <= 28:
                current_invest_value = cash * lot_percentage

                if cash > current_invest_value:
                    new_trade = AdditionalPosition(trade_id, LONG, current_invest_value, current_price, date)
                    trades.append(new_trade)
                    cash -= current_invest_value
                    position = LONG
                    trade_id += 1

        else:
            trade = trades[-1]

            if (
                    trade.get_current_win_percentage(current_price) > 1 and
                    end_of_positive_slope(prev_slope, cur_slope)
            ):
                trade.close(current_price, date, cash)
                position = None
                cash = trade.portfolio_value_after
                print(f"\n{trade}")

            if trade.should_create_additional_purchase(current_price):
                if trade.times_made_additional_purchase in list(range(6)) and rsi < 28:
                    if cash > current_invest_value:
                        trade.create_additional_purchase(current_price, current_invest_value, date)
                        cash -= current_invest_value


    Stats(initial_cash, lot_percentage, trades).export_stats_to_excel()
    plot_trades(df, trades)


def plot_trades(data, trades):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data.index, y=data.Close, mode='lines', name='Close'))
    fig.add_trace(go.Scatter(x=data.index, y=data[f'HMA_{HMA_PERIOD}'], name=f'HMA_{HMA_PERIOD}'))

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

            for purchase in trade.additional_purchases[1:]:  # Пропускаємо першу покупку (основну)
                fig.add_trace(go.Scatter(
                    x=[purchase.date], y=[purchase.open_price],
                    mode='markers',
                    marker=dict(color='blue', size=8, symbol='triangle-down'),
                    name=f'Additional Purchase Trade {trade.trade_id}'
                ))

    fig.update_layout(
        legend_title="Легенда",
        xaxis_rangeslider_visible=False,
        margin=dict(l=10, r=10, t=10, b=10),
        paper_bgcolor='white',
        height=600
    )

    fig.update_yaxes(title_text="Ціна")
    fig.show()

if __name__ == '__main__':
    filepath = '../custom_test_data/custom_csvs/AAVE_USDT_RECENT.csv'
    test_strategy(filepath)
