import plotly.graph_objects as go


def add_trades_marks(trades, fig):
    for trade in trades:
        if trade.closed:
            color = 'green' if trade.profit > 0 else 'red'

            fig.add_trace(go.Scatter(
                x=[trade.open_datetime], y=[trade.open_price],
                mode='markers',
                marker=dict(color=color, size=12),
                name=f'Відкриття trade {trade.trade_id}'
            ))

            fig.add_trace(go.Scatter(
                x=[trade.close_datetime], y=[trade.close_price],
                mode='markers',
                marker=dict(color=color, size=12),
                name=f'Закриття trade {trade.trade_id}'
            ))

            fig.add_trace(go.Scatter(
                x=[trade.open_datetime, trade.close_datetime],
                y=[trade.open_price, trade.close_price],
                mode='lines',
                line=dict(color=color, dash='dash'),
                name=f'Лінія trade {trade.trade_id}'
            ))

    return fig


def add_trades_marks_(trades, fig, row=1, col=1):
    for trade in trades:
        if trade.closed:
            color = 'green' if trade.profit > 0 else 'red'

            fig.add_trace(go.Scatter(
                x=[trade.open_datetime],
                y=[trade.open_price],
                mode='markers',
                marker=dict(color=color, size=12),
                name=f'Відкриття trade {trade.trade_id}'
            ), row=row, col=col)

            fig.add_trace(go.Scatter(
                x=[trade.close_datetime],
                y=[trade.close_price],
                mode='markers',
                marker=dict(color=color, size=12),
                name=f'Закриття trade {trade.trade_id}'
            ), row=row, col=col)

            fig.add_trace(go.Scatter(
                x=[trade.open_datetime, trade.close_datetime],
                y=[trade.open_price, trade.close_price],
                mode='lines',
                line=dict(color=color, dash='dash'),
                name=f'Лінія trade {trade.trade_id}'
            ), row=row, col=col)

    return fig
