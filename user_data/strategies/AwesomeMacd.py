# --- Do not remove these libs ---
from freqtrade.strategy import IStrategy, IntParameter, DecimalParameter, CategoricalParameter
from pandas import DataFrame
import talib.abstract as ta
import freqtrade.vendor.qtpylib.indicators as qtpylib


# --------------------------------


class AwesomeMacdBase(IStrategy):
    """
    Base class for AwesomeMacd strategy supporting multiple timeframes
    author@: Gert Wohlgemuth
    converted from: https://github.com/sthewissen/Mynt/blob/master/src/Mynt.Core/Strategies/AwesomeMacd.cs
    """
    INTERFACE_VERSION: int = 3
    
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
    roi_p1 = DecimalParameter(0.01, 0.10, default=0.05, space="roi", optimize=True)
    roi_p2 = DecimalParameter(0.01, 0.15, default=0.10, space="roi", optimize=True)
    roi_p3 = DecimalParameter(0.01, 0.30, default=0.15, space="roi", optimize=True)
    roi_p4 = DecimalParameter(0.01, 0.50, default=0.20, space="roi", optimize=True)
    
    # Stoploss hyperopt
    stoploss_opt = DecimalParameter(-0.50, -0.01, default=-0.10, space="stoploss", optimize=True)
    
    # Trailing stop hyperopt parameters
    trailing_stop_positive_opt = DecimalParameter(0.005, 0.05, default=0.02, space="stoploss", optimize=True)
    trailing_stop_positive_offset_opt = DecimalParameter(0.01, 0.10, default=0.04, space="stoploss", optimize=True)
    # Minimal ROI designed for the strategy.
    # adjust based on market conditions. We would recommend to keep it low for quick turn arounds
    # This attribute will be overridden if the config file contains "minimal_roi"
    # Minimal ROI designed for the strategy

    minimal_roi = {

        "0": 0.20,

        "20": 0.15,

        "30": 0.10,

        "60": 0.05

    }
    
    # Optimal stoploss designed for the strategy
    stoploss = -0.10

    # Timeframe will be set in subclasses
    
    # Trailing stop settings
    trailing_stop = True
    trailing_stop_positive = 0.02
    trailing_stop_positive_offset = 0.04
    trailing_only_offset_is_reached = True

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe['adx'] = ta.ADX(dataframe, timeperiod=14)
        dataframe['ao'] = qtpylib.awesome_oscillator(dataframe)

        macd = ta.MACD(dataframe)
        dataframe['macd'] = macd['macd']
        dataframe['macdsignal'] = macd['macdsignal']
        dataframe['macdhist'] = macd['macdhist']

        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
                    (dataframe['macd'] > 0) &
                    (dataframe['ao'] > 0) &
                    (dataframe['ao'].shift() < 0)

            ),
            'enter_long'] = 1
        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
                    (dataframe['macd'] < 0) &
                    (dataframe['ao'] < 0) &
                    (dataframe['ao'].shift() > 0)

            ),
            'exit_long'] = 1
        return dataframe


# 1分钟时间框架策略
class AwesomeMacd1m(AwesomeMacdBase):
    """
    AwesomeMacd strategy optimized for 1-minute timeframe
    """
    timeframe = '1m'
    
    # 1分钟优化的ROI设置
    minimal_roi = {
        "0": 0.10,
        "20": 0.08,
        "30": 0.05,
        "60": 0.02
    }
    
    # 1分钟优化的止损和追踪止损
    stoploss = -0.08
    trailing_stop_positive = 0.01
    trailing_stop_positive_offset = 0.025


# 5分钟时间框架策略
class AwesomeMacd5m(AwesomeMacdBase):
    """
    AwesomeMacd strategy optimized for 5-minute timeframe
    """
    timeframe = '5m'
    
    # 5分钟优化的ROI设置
    minimal_roi = {
        "0": 0.15,
        "20": 0.10,
        "30": 0.08,
        "60": 0.03
    }
    
    # 5分钟优化的止损和追踪止损
    stoploss = -0.10
    trailing_stop_positive = 0.02
    trailing_stop_positive_offset = 0.04


# 保持原有类名以向后兼容
class AwesomeMacd(AwesomeMacd5m):
    """
    Default AwesomeMacd strategy (5m timeframe for backward compatibility)
    """
    pass
