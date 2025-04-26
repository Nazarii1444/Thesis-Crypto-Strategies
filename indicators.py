import pandas as pd
import numpy as np


def add_rsi(df, period=14):
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    df[f'RSI_{period}'] = 100 - (100 / (1 + rs))
    return df


def add_macd(df, fast=12, slow=26, signal=9):
    ema_fast = df['Close'].ewm(span=fast, adjust=False).mean()
    ema_slow = df['Close'].ewm(span=slow, adjust=False).mean()
    df['MACD'] = ema_fast - ema_slow
    df['MACD_Signal'] = df['MACD'].ewm(span=signal, adjust=False).mean()
    df['MACD_Hist'] = df['MACD'] - df['MACD_Signal']
    return df


def add_bollinger_bands(df, period=20, std_dev=2):
    ma = df['Close'].rolling(window=period).mean()
    std = df['Close'].rolling(window=period).std()
    df['BB_Upper'] = ma + std_dev * std
    df['BB_Lower'] = ma - std_dev * std
    df['BB_Middle'] = ma
    return df


def add_atr(df, period=14):
    high_low = df['High'] - df['Low']
    high_close = np.abs(df['High'] - df['Close'].shift())
    low_close = np.abs(df['Low'] - df['Close'].shift())
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    df[f'ATR_{period}'] = tr.rolling(window=period).mean()
    return df


def add_stochastic_oscillator(df, k_period=14, d_period=3):
    low_min = df['Low'].rolling(window=k_period).min()
    high_max = df['High'].rolling(window=k_period).max()
    df['%K'] = 100 * ((df['Close'] - low_min) / (high_max - low_min))
    df['%D'] = df['%K'].rolling(window=d_period).mean()
    return df


def add_ma(df, period=14):
    df[f'MA_{period}'] = df['Close'].rolling(window=period).mean()
    return df


def add_ema(df, period=14):
    df[f'EMA_{period}'] = df['Close'].ewm(span=period, adjust=False).mean()
    return df


def add_wma(df, period=14):
    weights = np.arange(1, period + 1)

    def weighted_ma(x):
        return np.dot(x, weights) / weights.sum()

    df[f'WMA_{period}'] = df['Close'].rolling(window=period).apply(weighted_ma, raw=True)
    return df


def add_hma(df, period=14):
    half_length = int(period / 2)
    sqrt_length = int(np.sqrt(period))

    def wma(x):
        weights = np.arange(1, len(x) + 1)
        return np.dot(x, weights) / weights.sum()

    wma_half = df['Close'].rolling(window=half_length).apply(wma, raw=True)
    wma_full = df['Close'].rolling(window=period).apply(wma, raw=True)
    diff = 2 * wma_half - wma_full
    df[f'HMA_{period}'] = diff.rolling(window=sqrt_length).apply(wma, raw=True)
    return df


def add_adx(df, period=14):
    plus_dm = df['High'].diff()
    minus_dm = df['Low'].diff().abs()

    plus_dm = plus_dm.where((plus_dm > minus_dm) & (plus_dm > 0), 0.0)
    minus_dm = minus_dm.where((minus_dm > plus_dm) & (df['Low'].diff() > 0), 0.0)

    tr1 = df['High'] - df['Low']
    tr2 = (df['High'] - df['Close'].shift()).abs()
    tr3 = (df['Low'] - df['Close'].shift()).abs()
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

    atr = tr.rolling(window=period).mean()

    plus_di = 100 * (plus_dm.rolling(window=period).mean() / atr)
    minus_di = 100 * (minus_dm.rolling(window=period).mean() / atr)

    dx = (abs(plus_di - minus_di) / (plus_di + minus_di)) * 100
    df['ADX'] = dx.rolling(window=period).mean()
    return df


def add_cci(df, period=20):
    tp = (df['High'] + df['Low'] + df['Close']) / 3
    ma = tp.rolling(window=period).mean()
    md = tp.rolling(window=period).apply(lambda x: np.mean(np.abs(x - np.mean(x))), raw=True)
    df['CCI'] = (tp - ma) / (0.015 * md)
    return df


def add_roc(df, period=12):
    df['ROC'] = ((df['Close'] - df['Close'].shift(period)) / df['Close'].shift(period)) * 100
    return df


def add_trix(df, period=15):
    ema1 = df['Close'].ewm(span=period, adjust=False).mean()
    ema2 = ema1.ewm(span=period, adjust=False).mean()
    ema3 = ema2.ewm(span=period, adjust=False).mean()
    df['TRIX'] = ema3.pct_change() * 100
    return df


def add_obv(df):
    obv = [0]
    for i in range(1, len(df)):
        if df.loc[i, 'Close'] > df.loc[i - 1, 'Close']:
            obv.append(obv[-1] + df.loc[i, 'Volume'])
        elif df.loc[i, 'Close'] < df.loc[i - 1, 'Close']:
            obv.append(obv[-1] - df.loc[i, 'Volume'])
        else:
            obv.append(obv[-1])
    df['OBV'] = obv
    return df


def add_vwap(df):
    cumulative_vp = (df['Close'] * df['Volume']).cumsum()
    cumulative_volume = df['Volume'].cumsum()
    df['VWAP'] = cumulative_vp / cumulative_volume
    return df


def add_donchian_channels(df, period=20):
    df['Donchian_High'] = df['High'].rolling(window=period).max()
    df['Donchian_Low'] = df['Low'].rolling(window=period).min()
    df['Donchian_Mid'] = (df['Donchian_High'] + df['Donchian_Low']) / 2
    return df


def add_keltner_channel(df, period=20, atr_mult=2):
    typical_price = (df['High'] + df['Low'] + df['Close']) / 3
    tr1 = df['High'] - df['Low']
    tr2 = (df['High'] - df['Close'].shift()).abs()
    tr3 = (df['Low'] - df['Close'].shift()).abs()
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr = tr.rolling(window=period).mean()
    ma = typical_price.rolling(window=period).mean()
    df['Keltner_Upper'] = ma + atr_mult * atr
    df['Keltner_Lower'] = ma - atr_mult * atr
    df['Keltner_Mid'] = ma
    return df


def add_williams_r(df, period=14):
    highest_high = df['High'].rolling(window=period).max()
    lowest_low = df['Low'].rolling(window=period).min()
    df['Williams_%R'] = -100 * ((highest_high - df['Close']) / (highest_high - lowest_low))
    return df


def add_ad_line(df):
    mfm = ((df['Close'] - df['Low']) - (df['High'] - df['Close'])) / (df['High'] - df['Low'])
    mfv = mfm * df['Volume']
    df['AD_Line'] = mfv.cumsum()
    return df


def add_tema(df, period=20):
    ema1 = df['Close'].ewm(span=period, adjust=False).mean()
    ema2 = ema1.ewm(span=period, adjust=False).mean()
    ema3 = ema2.ewm(span=period, adjust=False).mean()
    df[f'TEMA_{period}'] = 3 * (ema1 - ema2) + ema3
    return df


def add_ichimoku(df):
    # Tenkan-sen (Conversion Line): (9-period high + 9-period low) / 2
    high_9 = df['High'].rolling(window=9).max()
    low_9 = df['Low'].rolling(window=9).min()
    df['Ichimoku_Tenkan'] = (high_9 + low_9) / 2

    # Kijun-sen (Base Line): (26-period high + 26-period low) / 2
    high_26 = df['High'].rolling(window=26).max()
    low_26 = df['Low'].rolling(window=26).min()
    df['Ichimoku_Kijun'] = (high_26 + low_26) / 2

    # Senkou Span A (Leading Span A): (Tenkan-sen + Kijun-sen) / 2, plotted 26 periods ahead
    df['Ichimoku_Senkou_A'] = ((df['Ichimoku_Tenkan'] + df['Ichimoku_Kijun']) / 2).shift(26)

    # Senkou Span B (Leading Span B): (52-period high + 52-period low) / 2, plotted 26 periods ahead
    high_52 = df['High'].rolling(window=52).max()
    low_52 = df['Low'].rolling(window=52).min()
    df['Ichimoku_Senkou_B'] = ((high_52 + low_52) / 2).shift(26)

    # Chikou Span (Lagging Span): Close shifted 26 periods back
    df['Ichimoku_Chikou'] = df['Close'].shift(-26)

    return df


def add_macross(df, short_period=12, long_period=26):
    df[f'MA_{short_period}'] = df['Close'].rolling(window=short_period).mean()
    df[f'MA_{long_period}'] = df['Close'].rolling(window=long_period).mean()
    df['MA_Cross'] = df[f'MA_{short_period}'] > df[f'MA_{long_period}']
    return df


def add_williams_alligator(df, jaw=13, teeth=8, lips=5):
    def smoothed_ma(series, period):
        return series.rolling(window=period).mean()

    df['Alligator_Jaw'] = smoothed_ma(df['Close'], jaw).shift(8)
    df['Alligator_Teeth'] = smoothed_ma(df['Close'], teeth).shift(5)
    df['Alligator_Lips'] = smoothed_ma(df['Close'], lips).shift(3)
    return df
