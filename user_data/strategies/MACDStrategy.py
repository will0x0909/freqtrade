
# --- Do not remove these libs ---
from freqtrade.strategy import IStrategy
from freqtrade.strategy import CategoricalParameter, DecimalParameter, IntParameter
from pandas import DataFrame
# --------------------------------

import talib.abstract as ta


class MACDStrategyBase(IStrategy):
    """
    Base class for MACDStrategy supporting multiple timeframes
    author@: Gert Wohlgemuth

    idea:
        uptrend definition: MACD above MACD signal and CCI < -50
        downtrend definition: MACD below MACD signal and CCI > 100
    """
    INTERFACE_VERSION: int = 3

    # Minimal ROI designed for the strategy.
    # This attribute will be overridden if the config file contains "minimal_roi"
    minimal_roi = {
        "0": 0.119,
        "39": 0.047,
        "92": 0.018,
        "167": 0
    }

    # Optimal stoploss designed for the strategy
    # This attribute will be overridden if the config file contains "stoploss"
    stoploss = -0.206
    
    # Trailing stop settings
    trailing_stop = True
    trailing_stop_positive = 0.02  # Start trailing when profit is 2%
    trailing_stop_positive_offset = 0.04  # Trail 4% below high
    trailing_only_offset_is_reached = True  # Only start trailing after positive offset is reached
    
    # Timeframe will be set in subclasses

    buy_cci = IntParameter(low=-700, high=0, default=-50, space='buy', optimize=True)
    sell_cci = IntParameter(low=0, high=700, default=100, space='sell', optimize=True)

    # Buy hyperspace params:
    buy_params = {
        "buy_cci": -58,
    }

    # Sell hyperspace params:
    sell_params = {
        "sell_cci": 131,
    }

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:

        macd = ta.MACD(dataframe)
        dataframe['macd'] = macd['macd']
        dataframe['macdsignal'] = macd['macdsignal']
        dataframe['macdhist'] = macd['macdhist']
        dataframe['cci'] = ta.CCI(dataframe)

        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Based on TA indicators, populates the buy signal for the given dataframe
        :param dataframe: DataFrame
        :return: DataFrame with buy column
        """
        dataframe.loc[
            (
                (dataframe['macd'] > dataframe['macdsignal']) &
                (dataframe['cci'] <= self.buy_cci.value) &
                (dataframe['volume'] > 0)  # Make sure Volume is not 0
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
                (dataframe['macd'] < dataframe['macdsignal']) &
                (dataframe['cci'] >= self.sell_cci.value) &
                (dataframe['volume'] > 0)  # Make sure Volume is not 0
            ),
            'exit_long'] = 1

        return dataframe


# 1分钟时间框架策略
class MACDStrategy1m(MACDStrategyBase):
    """
    MACDStrategy optimized for 1-minute timeframe
    """
    timeframe = '1m'
    
    # 1分钟优化的ROI设置
    minimal_roi = {
        "0": 0.08,
        "39": 0.03,
        "92": 0.015,
        "167": 0
    }
    
    # 1分钟优化的止损和追踪止损
    stoploss = -0.15
    trailing_stop_positive = 0.01
    trailing_stop_positive_offset = 0.02


# 5分钟时间框架策略
class MACDStrategy5m(MACDStrategyBase):
    """
    MACDStrategy optimized for 5-minute timeframe
    """
    timeframe = '5m'
    
    # 5分钟优化的ROI设置
    minimal_roi = {
        "0": 0.119,
        "39": 0.047,
        "92": 0.018,
        "167": 0
    }
    
    # 5分钟优化的止损和追踪止损  
    stoploss = -0.206
    trailing_stop_positive = 0.02
    trailing_stop_positive_offset = 0.04


# 保持原有类名以向后兼容
class MACDStrategy(MACDStrategy5m):
    """
    Default MACDStrategy (5m timeframe for backward compatibility)
    """
    pass
