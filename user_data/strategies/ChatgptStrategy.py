# Three Freqtrade strategies tuned for 5m long-only trading on low-liquidity "alpha" tokens.
# Save this file into your freqtrade project's user_data/strategies folder.
# Notes:
# - Timeframe = 5m
# - These are LONG-only strategies (no short). Set "can_short = False".
# - Make sure exchange/trading pair exists and that you have enough balance/fee token.
# - Always backtest thoroughly and tweak parameters for each token.

from freqtrade.strategy.interface import IStrategy
from pandas import DataFrame
import pandas as pd
import numpy as np


# ------------------ utilities ------------------

def vwap(df: DataFrame, period: int = None) -> pd.Series:
    # VWAP over the whole dataframe (or rolling window if period provided)
    typical = (df['high'] + df['low'] + df['close']) / 3
    vol = df['volume']
    tpv = typical * vol
    if period is None:
        return tpv.cumsum() / vol.cumsum()
    else:
        return tpv.rolling(period).sum() / vol.rolling(period).sum()


def kama(series: pd.Series, er_window: int = 10, fast: int = 2, slow: int = 30) -> pd.Series:
    # Simple KAMA implementation
    # Efficiency Ratio (ER)
    change = series.diff(er_window).abs()
    volatility = series.diff().abs().rolling(er_window).sum()
    er = change / (volatility.replace(0, np.nan))
    fast_sc = 2/(fast+1)
    slow_sc = 2/(slow+1)
    sc = (er*(fast_sc - slow_sc) + slow_sc) ** 2
    kama = [np.nan] * len(series)
    # initialize with first value
    kama[er_window] = series.iloc[:er_window+1].mean()
    for i in range(er_window+1, len(series)):
        kama[i] = kama[i-1] + sc.iat[i] * (series.iat[i] - kama[i-1])
    return pd.Series(kama, index=series.index)


def atr(df: DataFrame, period: int = 14) -> pd.Series:
    high_low = df['high'] - df['low']
    high_close = (df['high'] - df['close'].shift()).abs()
    low_close = (df['low'] - df['close'].shift()).abs()
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    return tr.rolling(period).mean()


def mfi(df: DataFrame, period: int = 14) -> pd.Series:
    typical = (df['high'] + df['low'] + df['close']) / 3
    raw_money = typical * df['volume']
    sign = typical.diff().fillna(0).apply(lambda x: 1 if x>0 else (-1 if x<0 else 0))
    pos = raw_money.where(sign>0, 0).rolling(period).sum()
    neg = raw_money.where(sign<0, 0).abs().rolling(period).sum()
    mfr = pos / (neg.replace(0, np.nan))
    mfi = 100 - (100 / (1 + mfr))
    return mfi


# ------------------ Strategy A: Momentum (VWAP + Volume Spike + KAMA + ATR stop) ------------------
class AlphaMomentumVWAP(IStrategy):
    INTERFACE_VERSION = 3

    # Strategy settings
    timeframe = '5m'
    can_short = False
    minimal_roi = {"0": 0.10, "30": 0.05, "120": 0.02}  # example, tweak by backtest
    stoploss = -0.10  # baseline, will be managed with atr-based dynamic stop
    trailing_stop = False

    # parameters
    vwap_window = 50  # rolling VWAP window in bars
    vol_window = 20
    vol_spike_mult = 2.0
    kama_er = 10
    atr_period = 14
    mfi_period = 14

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        df = dataframe.copy()
        df['vwap'] = vwap(df, period=self.vwap_window)
        df['kama'] = kama(df['close'], er_window=self.kama_er, fast=2, slow=30)
        df['atr'] = atr(df, period=self.atr_period)
        df['mfi'] = mfi(df, period=self.mfi_period)
        df['vol_mean'] = df['volume'].rolling(self.vol_window).mean()
        df['vol_spike'] = df['volume'] > (df['vol_mean'] * self.vol_spike_mult)
        # short-term momentum
        df['close_sma5'] = df['close'].rolling(5).mean()
        return df

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        df = dataframe.copy()
        df['enter_long'] = (
            (df['close'] > df['vwap']) &
            (df['vol_spike']) &
            (df['mfi'] > 55) &
            (df['kama'] > df['kama'].shift(1)) &
            (df['close'] > df['close_sma5'])
        )
        dataframe['enter_long'] = df['enter_long']
        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        df = dataframe.copy()
        # Exit when price drops below VWAP or MFI turns down, or ATR-based stoploss handled by freqtrade stoploss
        df['exit_long'] = (
            (df['close'] < df['vwap']) |
            (df['mfi'] < 40)
        )
        dataframe['exit_long'] = df['exit_long']
        return dataframe


# ------------------ Strategy B: Aggressive VWAP Pullback + Volume Confirmation ------------------
class AlphaVWAPPullback(IStrategy):
    INTERFACE_VERSION = 3
    timeframe = '5m'
    can_short = False
    minimal_roi = {"0": 0.12, "20": 0.06, "100": 0.02}
    stoploss = -0.12
    trailing_stop = True
    trailing_stop_positive = 0.02
    trailing_stop_positive_offset = 0.03

    vwap_window = 100
    vol_window = 20
    vol_spike_mult = 1.8
    atr_period = 14

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        df = dataframe.copy()
        df['vwap'] = vwap(df, period=self.vwap_window)
        df['atr'] = atr(df, period=self.atr_period)
        df['vol_mean'] = df['volume'].rolling(self.vol_window).mean()
        df['vol_spike'] = df['volume'] > (df['vol_mean'] * self.vol_spike_mult)
        # measure distance to vwap
        df['dist_vwap'] = (df['close'] - df['vwap']) / df['vwap']
        df['sma9'] = df['close'].rolling(9).mean()
        return df

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        df = dataframe.copy()
        # buy the dip while above VWAP and with volume confirmation and quick rebound
        df['enter_long'] = (
            (df['dist_vwap'] > -0.03) &  # not too far below vwap (within 3%)
            (df['close'] > df['sma9']) &
            (df['vol_spike'])
        )
        dataframe['enter_long'] = df['enter_long']
        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        df = dataframe.copy()
        df['exit_long'] = (
            (df['close'] < df['vwap']) |
            (df['dist_vwap'] > 0.08)  # take profit if 8% above vwap
        )
        dataframe['exit_long'] = df['exit_long']
        return dataframe


# ------------------ Strategy C: Mean Reversion (contrarian, low-liquidity capture) ------------------
class AlphaMeanReversion(IStrategy):
    INTERFACE_VERSION = 3
    timeframe = '5m'
    can_short = False
    minimal_roi = {"0": 0.08, "60": 0.04, "240": 0.01}
    stoploss = -0.08
    trailing_stop = False

    vwap_window = 50
    mfi_period = 8
    atr_period = 14

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        df = dataframe.copy()
        df['vwap'] = vwap(df, period=self.vwap_window)
        df['mfi'] = mfi(df, period=self.mfi_period)
        df['atr'] = atr(df, period=self.atr_period)
        df['vol_mean20'] = df['volume'].rolling(20).mean()
        return df

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        df = dataframe.copy()
        # Buy when price dips well below VWAP but volume is low (suggests temporary washout)
        df['enter_long'] = (
            (df['close'] < df['vwap'] * 0.985) &  # ~1.5% below vwap
            (df['mfi'] < 30) &
            (df['volume'] < df['vol_mean20'] * 1.0)  # not a huge sell-off volume
        )
        dataframe['enter_long'] = df['enter_long']
        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        df = dataframe.copy()
        # Exit when price returns above VWAP or MFI recovers
        df['exit_long'] = (
            (df['close'] > df['vwap']) |
            (df['mfi'] > 55)
        )
        dataframe['exit_long'] = df['exit_long']
        return dataframe


# ------------------ End of strategies ------------------
# Remember:
# - These are starting templates. You MUST backtest with your universe and refine params.
# - Consider slippage, exchange fees, and minimum trade size for low-liquidity tokens.
# - Add safety filters (e.g., minimum 24h volume, max spread) in your pairlist configuration.
# - Use small position sizing and strict risk management for alpha tokens.
