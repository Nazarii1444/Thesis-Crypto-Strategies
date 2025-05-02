import io
from datetime import datetime

import mplfinance as mpf
import pandas as pd
from utils.indicators import add_hma
from pybit.unified_trading import HTTP

from config import Config
from logger import logger
from tg_bot_operations import send_message

config_ = Config()
session = HTTP(
    api_key=config_.bybit_api_key,
    api_secret=config_.bybit_api_secret,
    recv_window=50000, max_retries=3,
)

# Open positions example:
# [{'symbol': 'AAVEUSDT','leverage': '1', 'autoAddMargin': 0,
# 'avgPrice': '138.36', 'liqPrice': '654.75295633',
# 'riskLimitValue': '200000', 'takeProfit': '137.98',
# 'positionValue': '23.5212', 'isReduceOnly': False,
# 'tpslMode': 'Full', 'riskId': 191, 'trailingStop': '0',
# 'unrealisedPnl': '-0.5338', 'markPrice': '141.5',
# 'adlRankIndicator': 2, 'cumRealisedPnl': '-1.68726666',
# 'positionMM': '0.5174664', 'createdTime': '1727283463319',
# 'positionIdx': 0, 'positionIM': '23.5682424', 'seq': 119160992297,
# 'updatedTime': '1727876403679', 'side': 'Sell', 'bustPrice': '',
# 'positionBalance': '0', 'leverageSysUpdatedTime': '',
# 'curRealisedPnl': '-0.0235212', 'size': '0.17',
# 'positionStatus': 'Normal', 'mmrSysUpdatedTime': '',
# 'stopLoss': '142.71', 'tradeMode': 0, 'sessionAvgPrice': ''}]


def get_balance():
    try:
        resp = session.get_wallet_balance(
            accountType="UNIFIED", coin="USDT"
        )['result']['list'][0]['coin'][0]['walletBalance']
        logger.info(f'BALANCE: {resp}')
        return float(resp), f"BALANCE: {float(resp):.2f}"
    except Exception as err:
        logger.info(f"An exception occured in GET_BALANCE: {err}")
        send_message(f"An exception occured in GET_BALANCE: {err}")


def set_leverage_(symbol, leverage="1"):
    try:
        resp = session.set_leverage(
            category="linear",
            symbol=symbol,
            buyLeverage=leverage,
            sellLeverage=leverage
        )
        logger.info('LEVERAGE SET')
        return resp
    except Exception as err:
        logger.info(f"An exception occured in SET_LEVERAGE: {err}")
        send_message(f"An exception occured in SET_LEVERAGE: {err}")


def get_klines(symbol, timeframe="30", limit=400):
    try:
        data = session.get_kline(
            category='linear',
            symbol=symbol,
            interval=timeframe,
            limit=limit,
        )['result']['list']

        formatted_data = pd.DataFrame(map(lambda item: {
            'Date': datetime.fromtimestamp(int(item[0]) / 1000).strftime('%Y-%m-%d %H:%M:%S'),
            'Open': float(item[1]),
            'High': float(item[2]),
            'Low': float(item[3]),
            'Close': float(item[4]),
            'Volume': float(item[5])
        }, data))[::-1]

        formatted_data = add_hma(formatted_data, config_.hma_period)
        formatted_data["SLOPE"] = formatted_data["HMA"].diff()

        return formatted_data
    except Exception as err:
        logger.info(f"An exception occured in GET_KLINES: {err}")
        send_message(f"An exception occured in GET_KLINES: {err}")
        return pd.DataFrame({})


def prepare_plot(data, avg_price):
    try:
        buf = io.BytesIO()

        data = data[150:]

        data['Date'] = pd.to_datetime(data['Date'])
        data.set_index('Date', inplace=True)

        to_num = ['Open', 'High', 'Low', 'Close', 'Volume']
        data[to_num] = data[to_num].apply(pd.to_numeric, errors='coerce')
        data.dropna(subset=to_num, inplace=True)

        data["HMA"] = data["HMA"].bfill()
        data["SLOPE"] = data["SLOPE"].bfill()

        add_plots = [mpf.make_addplot(data.HMA, color='#f59542', width=1.1, label='HMA')]

        mc = mpf.make_marketcolors(up='#3ade6e', down='#de453a', inherit=True)
        s = mpf.make_mpf_style(
            marketcolors=mc,
            facecolor='#000000',
            edgecolor='#000000',
            gridcolor='#444444',
            rc={
                'axes.labelcolor': '#FFFFFF',
                'xtick.color': '#FFFFFF',
                'ytick.color': '#FFFFFF',
                'figure.facecolor': '#000000',
                'legend.facecolor': '#1E1E1E',
                'legend.edgecolor': '#FFFFFF',
                'legend.labelcolor': '#FFFFFF'
            }
        )

        legend_labels = []
        add_plots.append(
            mpf.make_addplot([avg_price] * len(data), color='lime', label=f'Avg price: {avg_price}')
        )

        plot_kwargs = {
            'type': 'candle',
            'style': s,
            'ylabel': 'Price',
            'volume': False,
            'addplot': add_plots,
            'figsize': (15, 10),
            'tight_layout': True,
            'datetime_format': '%m-%d %H:%M',
            'savefig': dict(fname=buf, format='png'),
            'returnfig': True
        }

        fig, axlist = mpf.plot(data, **plot_kwargs)
        axlist[0].legend(legend_labels, loc='upper left')

        buf.seek(0)
        return buf
    except Exception as err:
        logger.info(f"An exception occured in PREPARE_PLOT: {err}")
        send_message(f"An exception occured in PREPARE_PLOT: {err}")


def get_positions():
    try:
        resp = session.get_positions(category='linear', settleCoin='USDT')['result']['list']
        return resp
    except Exception as err:
        logger.info(f"An exception occured in GET_POSITIONS: {err}")
        send_message(f"An exception occured in GET_POSITIONS: {err}")


def set_tp_sl(order_id: str, symbol: str, tp_price: float, sl_price: float):
    try:
        res = session.amend_order(
            category='linear',
            symbol=symbol,
            orderId=order_id,
            takeProfit=str(tp_price),
            stopLoss=str(sl_price),
        )
        return res
    except Exception as err:
        logger.error(f"An exception occured in set_tp_sl: {err}")
        send_message(f"An exception occured in set_tp_sl: {err}")


def open_long_trade(symbol: str, tp_price: float, sl_price: float):
    try:
        # cash, msg = get_balance()
        order_qty = 0.04

        try:
            logger.info(f'open_long_trade()')

            resp = session.place_order(
                category='linear',
                symbol=symbol,
                side='Buy',
                orderType='Market',
                qty=order_qty,
                takeProfit=str(tp_price),
                stopLoss=str(sl_price),
                timeInForce="GTC"
            )
            logger.info(f'OPENED LONG TRADE FOR SYMBOL {symbol} ')
            return resp
        except Exception as err:
            logger.info(f"An exception occured in OPEN_LONG_TRADE:\n {err}")
    except Exception as err:
        send_message(f"Exception occured in OPEN_LONG_TRADE: \n{err}")


def open_short_trade(symbol: str, tp_price: float, sl_price: float):
    try:
        # cash, msg = get_balance()
        order_qty = 0.04

        try:
            logger.info(f'open_short_trade()')

            resp = session.place_order(
                category='linear',
                symbol=symbol,
                side='Sell',
                orderType='Market',
                qty=order_qty,
                takeProfit=str(tp_price),
                stopLoss=str(sl_price),
                timeInForce="GTC"
            )

            logger.info(f'OPENED SHORT TRADE FOR SYMBOL {symbol} ')
            return resp
        except Exception as err:
            logger.info(f"An exception occured in OPEN_SHORT_TRADE:\n {err}")
    except Exception as err:
        send_message(f"Exception occured in OPEN_SHORT_TRADE: \n{err}")


def close_current_position(symbol: str, qty: int, side: str):
    invertor = {'Buy': 'Sell', 'Sell': 'Buy'}
    inverted_side = invertor[side]

    try:
        resp = session.place_order(
            category='linear',
            symbol=symbol,
            side=inverted_side,
            orderType='Market',
            qty=str(qty)
        )
        logger.info(f'Closed {side.upper()} | {qty}')
        return True
    except Exception as err:
        logger.info(f"An exception occured in close_current_position: {err}")
        send_message(f"An exception occured in close_current_position: {err}")
        return False


def get_mark_price(symbol: str):
    try:
        mark_price = float(session.get_tickers(
            category='linear',
            symbol=symbol
        )['result']['list'][0]['markPrice'])

        return mark_price
    except Exception as err:
        logger.info(f"An exception occured in GET_MARK_PRICE: {err}")
        send_message(f"An exception occured in GET_MARK_PRICE: {err}")


def transform_datetime(value):
    return datetime.fromtimestamp(int(value) / 1000).strftime('%Y-%m-%d %H:%M:%S')


def str_trade(trade_dict):
    if trade_dict is not None:
        try:
            return (
                f"symbol: {trade_dict.get('symbol', 0)}\n"
                f"avg price: {trade_dict.get('avgPrice', 0)}\n"
                f"qty: {trade_dict.get('size', 0)}"
                f"value: {trade_dict.get('positionValue', 0)}\n"
                f"CumRealisedPnl: {trade_dict.get('cumRealisedPnl', 0)}\n"
                f"liqPrice: {trade_dict.get('liqPrice', 0)}"
            )
        except Exception as err:
            logger.info(f"An exception occured in STR_TRADE: {err}")
            send_message(f"An exception occured in STR_TRADE: {err}")
    else:
        msg = "ELSE in str_trade: trade_dict is None"
        logger.info(msg)
        send_message(msg)


def open_long_limit_order(symbol: str, price: float):
    try:
        cash, msg = get_balance()
        order_qty = 0.04

        try:
            logger.info(f'open_long_limit_trade()')

            resp = session.place_order(
                category='linear',
                symbol=symbol,
                price=str(price),
                side='Buy',
                orderType='Limit',
                qty=order_qty,
            )

            logger.info(f'OPENED LIMIT LONG TRADE FOR SYMBOL {symbol} ')
            return resp
        except Exception as err:
            logger.info(f"An exception occured in OPEN_LONG_LIMIT_ORDER: {msg} \n {err}")
            return f"An exception occured in OPEN_LONG_LIMIT_ORDER: {msg} \n {err}"
    except Exception as err:
        send_message(f"Exception occured in OPEN_LONG_LIMIT_ORDER: \n{err}")


def open_short_limit_order(symbol: str, price: float):
    try:
        cash, msg = get_balance()
        order_qty = 0.04

        try:
            logger.info(f'open_short_limit_trade()')

            resp = session.place_order(
                category='linear',
                symbol=symbol,
                price=str(price),
                side='Sell',
                orderType='Limit',
                qty=order_qty,
                timeInForce='IOC'
            )

            logger.info(f'OPENED LIMIT SHORT TRADE FOR SYMBOL {symbol} ')
        except Exception as err:
            logger.info(f"An exception occured in OPEN_SHORT_LIMIT_TRADE: {msg} \n {err}")
            return f"An exception occured in OPEN_SHORT_LIMIT_TRADE: {msg} \n {err}"
    except Exception as err:
        send_message(f"Exception occured in OPEN_SHORT_LIMIT_TRADE: \n{err}")


def get_orderbook(symbol: str):
    try:
        ob = session.get_orderbook(
            category='linear',
            symbol=symbol,
            limit=500
        )['result']

        bids_df = pd.DataFrame(ob['b'], columns=["price", "qty"]).astype(float)
        asks_df = pd.DataFrame(ob['a'], columns=["price", "qty"]).astype(float)

        # whole_df = pd.concat([asks_df[::-1], bids_df], axis=0).reset_index(drop=True)

        return asks_df[::-1], bids_df
    except Exception as err:
        print(f"An exception occured in GET_ORDERBOOK: {err}")


def best_long_price(asks_df, bids_df):
    return asks_df.iloc[-1]['price']


def best_short_price(asks_df, bids_df):
    return bids_df.iloc[0]['price']


def get_open_orders(symbol: str):
    try:
        resp = session.get_open_orders(category='linear', symbol=symbol)['result']['list']
        return resp
    except Exception as err:
        logger.error(f"An exception occured in GET_OPEN_ORDERS: {err}")
        send_message(f"An exception occured in GET_OPEN_ORDERS: {err}")


def cancel_all_orders(symbol: str):
    try:
        resp = session.cancel_all_orders(category='linear', symbol=symbol)
        return resp
    except Exception as err:
        logger.error(f"An exception occured in cancel_all_orders: {err}")
        send_message(f"An exception occured in cancel_all_orders: {err}")


def get_trade_history(symbol='AAVEUSDT', category='linear'):
    try:
        resp = session.get_executions(
            category=category, symbol=symbol
        )['result']['list']
        return resp
    except Exception as err:
        logger.error(f"An exception occured in get_instruments_info: {err}")


def get_account_info():
    try:
        resp = session.get_account_info()
        return resp['result']
    except Exception as err:
        logger.error(f"An exception occured in get_account_info: {err}")


def closed_pnl():
    try:
        resp = session.get_closed_pnl(
            category='linear',
            symbol='AAVEUSDT',
            limit=1
        )['result']['list'][0]
        return resp
    except Exception as err:
        logger.error(f"An exception occured in closed_pnl: {err}")


def get_last_closed_pnl():
    return float(closed_pnl()['closedPnl'])


if __name__ == '__main__':
    res = get_last_closed_pnl()
    print(res)
