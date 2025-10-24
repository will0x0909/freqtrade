# --- Do not remove these libs ---
from freqtrade.strategy import IStrategy, IntParameter, DecimalParameter, CategoricalParameter
from typing import Dict, List
from functools import reduce
from pandas import DataFrame
# --------------------------------

import talib.abstract as ta
import freqtrade.vendor.qtpylib.indicators as qtpylib


class MACDStrategy_crossed1m(IStrategy):
    """
    MACDStrategy_crossed optimized for 1-minute timeframe
    buy: MACD crosses MACD signal above and CCI < -50
    sell: MACD crosses MACD signal below and CCI > 100
    """
    INTERFACE_VERSION: int = 3
    
    # Timeframe for this strategy
    timeframe = '1m'
    
    # Hyperopt parameters
    buy_rsi_threshold = IntParameter(20, 40, default=30, space="buy", optimize=True)
    buy_macd_threshold = DecimalParameter(-0.02, 0.02, default=0, space="buy", optimize=True)
    buy_bb_multiplier = DecimalParameter(0.8, 1.2, default=1.0, space="buy", optimize=True)
    
    sell_rsi_threshold = IntParameter(60, 80, default=70, space="sell", optimize=True)
    sell_macd_threshold = DecimalParameter(-0.02, 0.02, default=0, space="sell", optimize=True)
    sell_bb_multiplier = DecimalParameter(0.8, 1.2, default=1.0, space="sell", optimize=True)
    
    # ROI table hyperopt
    roi_t1 = IntParameter(10, 120, default=60, space="roi", optimize=True)
    roi_t2 = IntParameter(10, 60, default=30, space="roi", optimize=True)  
    roi_t3 = IntParameter(5, 40, default=20, space="roi", optimize=True)
    roi_p1 = DecimalParameter(0.01, 0.08, default=0.02, space="roi", optimize=True)
    roi_p2 = DecimalParameter(0.01, 0.10, default=0.05, space="roi", optimize=True)
    roi_p3 = DecimalParameter(0.01, 0.15, default=0.08, space="roi", optimize=True)
    roi_p4 = DecimalParameter(0.01, 0.25, default=0.12, space="roi", optimize=True)
    
    # Stoploss hyperopt
    stoploss_opt = DecimalParameter(-0.50, -0.01, default=-0.08, space="stoploss", optimize=True)
    
    # Trailing stop hyperopt parameters
    trailing_stop_positive_opt = DecimalParameter(0.005, 0.05, default=0.01, space="stoploss", optimize=True)
    trailing_stop_positive_offset_opt = DecimalParameter(0.01, 0.10, default=0.025, space="stoploss", optimize=True)

    # 1分钟优化的ROI设置
    minimal_roi = {
        "0": 0.12,
        "20": 0.08,
        "30": 0.05,
        "60": 0.02
    }
    
    # 1分钟优化的止损和追踪止损
    stoploss = -0.08
    
    # Trailing stop settings
    trailing_stop = True
    trailing_stop_positive = 0.01
    trailing_stop_positive_offset = 0.025
    trailing_only_offset_is_reached = True

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:

        macd = ta.MACD(dataframe, fastperiod=12, slowperiod=26, signalperiod=9)
        dataframe['macd'] = macd['macd']
        dataframe['macdsignal'] = macd['macdsignal']
        dataframe['macdhist'] = macd['macdhist']
        dataframe['cci'] = ta.CCI(dataframe, timeperiod=14)

        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Based on TA indicators, populates the buy signal for the given dataframe
        :param dataframe: DataFrame
        :return: DataFrame with buy column
        """
        dataframe.loc[
            (
                qtpylib.crossed_above(dataframe['macd'], dataframe['macdsignal']) &
                (dataframe['cci'] <= -50.0)
            ),
            'enter_long'] = 1

        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Based on TA indicators, populates the sell signal for the given dataframe
        :param dataframe: DataFrame
        :return: DataFrame with buy column
        """
        dataframe.loc[
            (
                qtpylib.crossed_below(dataframe['macd'], dataframe['macdsignal']) &
                (dataframe['cci'] >= 100.0)
            ),
            'exit_long'] = 1

        return dataframe