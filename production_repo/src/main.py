from bybit_conn import get_klines
from config import Config
from logger import logger
from tg_bot_operations import send_message
from concurrent.futures import ThreadPoolExecutor
from waiting import wait_for_next_30_minute_cycle

LONG, SHORT = 'LONG', 'SHORT'
config_ = Config()


def end_of_positive_slope(slope_value, prev_slope_value):
    return prev_slope_value > 0 > slope_value


def end_of_negative_slope(slope_value, prev_slope_value):
    return prev_slope_value < 0 < slope_value


SYMBOLS = [
    "BTCUSDT", "ETHUSDT", "XRPUSDT", "SOLUSDT",
    "DOGEUSDT", "WIFUSDT", "LTCUSDT", "AAVEUSDT",
    "BNBUSDT", "DOTUSDT", "ADAUSDT", "LINKUSDT"
]


def check_slope(symbol):
    data = get_klines(symbol)
    if data.empty or data is None:
        return None, None

    prev_slope_value = data["SLOPE"].iloc[-2]
    slope_value = data["SLOPE"].iloc[-1]

    if end_of_positive_slope(slope_value, prev_slope_value):
        return symbol, "🔴 END OF POSITIVE SLOPE"
    elif end_of_negative_slope(slope_value, prev_slope_value):
        return symbol, "🟢 END OF NEGATIVE SLOPE"
    return None, None


def main_run():
    send_message(f"! Starting slope screener")

    while True:
        messages = []
        with ThreadPoolExecutor(max_workers=len(SYMBOLS)) as executor:
            results = executor.map(check_slope, SYMBOLS)

        for symbol, message in results:
            if message:
                messages.append(f"{symbol}: {message}")

        if messages:
            to_send = "\n".join(messages)
        else:
            to_send = "! No slope"

        send_message(to_send)
        wait_for_next_30_minute_cycle()


if __name__ == '__main__':
    try:
        main_run()
    except Exception as e:
        logger.error(e)
        send_message(e)
