# pragma pylint: disable=missing-docstring, invalid-name, pointless-string-statement
# flake8: noqa: F401
# isort: skip_file
# --- Do not remove these libs ---
import numpy as np
import pandas as pd
from pandas import DataFrame
from datetime import datetime
from typing import Optional, Union

from freqtrade.strategy import (BooleanParameter, CategoricalParameter, DecimalParameter,
                                IntParameter, IStrategy, merge_informative_pair)

# --------------------------------
# Add your lib to import here
import talib.abstract as ta
import pandas_ta as pta
from technical import qtpylib


class UniversalMACD5m(IStrategy):
    # By: Masoud Azizi (@mablue)
    # Tradingview Page: https://www.tradingview.com/script/xNEWcB8s-Universal-Moving-Average-Convergence-Divergence/
    # Optimized for 5-minute timeframe

    # Strategy interface version - allow new iterations of the strategy interface.
    # Check the documentation or the Sample strategy to get the latest version.
    INTERFACE_VERSION = 3

    # Timeframe for this strategy
    timeframe = '5m'
    
    # Can this strategy go short?
    can_short: bool = False

    # 5分钟优化的ROI设置
    minimal_roi = {
        "0": 0.15,
        "20": 0.08,
        "40": 0.03,
        "60": 0
    }

    # Stoploss:
    stoploss = -0.10

    # Trailing stop settings
    trailing_stop = True
    trailing_stop_positive = 0.02
    trailing_stop_positive_offset = 0.04
    trailing_only_offset_is_reached = True

    # Number of candles the strategy requires before producing valid signals
    startup_candle_count: int = 30

    # Strategy parameters
    buy_umacd_max = DecimalParameter(-0.05, 0.05, decimals=5, default=-0.01176, space="buy")
    buy_umacd_min = DecimalParameter(-0.05, 0.05, decimals=5, default=-0.01416, space="buy")
    sell_umacd_max = DecimalParameter(-0.05, 0.05, decimals=5, default=-0.02323, space="sell")
    sell_umacd_min = DecimalParameter(-0.05, 0.05, decimals=5, default=-0.00707, space="sell")

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe['ma12'] = ta.EMA(dataframe, timeperiod=12)
        dataframe['ma26'] = ta.EMA(dataframe, timeperiod=26)
        dataframe['umacd'] = (dataframe['ma12'] / dataframe['ma26']) - 1

        # Just for show user the min and max of indicator in different coins to set inside hyperoptable variables.cuz
        # in different timeframes should change the min and max in hyperoptable variables.
        # print(dataframe['umacd'].min(), dataframe['umacd'].max())

        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
                (dataframe['umacd'].between(self.buy_umacd_min.value, self.buy_umacd_max.value))

            ),
            'enter_long'] = 1

        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
                (dataframe['umacd'].between(self.sell_umacd_min.value, self.sell_umacd_max.value))
            ),
            'exit_long'] = 1

        return dataframe