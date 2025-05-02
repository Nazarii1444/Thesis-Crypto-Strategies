import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    def __init__(self):
        # SECRETS
        self._bybit_api_key = os.getenv('BYBIT_API_KEY')
        self._bybit_api_secret = os.getenv('BYBIT_API_SECRET')
        self._telegram_api_key = os.getenv('TELEGRAM_API_KEY')
        self._xtayl_events = os.getenv('XTAYL_EVENTS')
        self._chat_id = os.getenv('CHAT_ID')
        self._group_id = os.getenv('GROUP_ID')

        # TRADING CONFIG
        self._main_symbol = "AAVEUSDT"
        self._rsi = 28
        self._rsi_period = 18
        self._hma_period = 25

    @property
    def bybit_api_key(self):
        return self._bybit_api_key

    @property
    def bybit_api_secret(self):
        return self._bybit_api_secret

    @property
    def telegram_api_key(self):
        return self._telegram_api_key

    @property
    def xtayl_events(self):
        return self._xtayl_events

    @property
    def chat_id(self):
        return self._chat_id

    @property
    def group_id(self):
        return self._group_id

    @property
    def main_symbol(self):
        return self._main_symbol

    @property
    def rsi(self):
        return self._rsi

    @property
    def rsi_period(self):
        return self._rsi_period

    @property
    def hma_period(self):
        return self._hma_period
