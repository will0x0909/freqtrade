# --- Do not remove these libs ---
import freqtrade.vendor.qtpylib.indicators as qtpylib
import talib.abstract as ta
from freqtrade.strategy import IStrategy
from freqtrade.strategy import IntParameter
from pandas import DataFrame


# --------------------------------


class CofiBitStrategyBase(IStrategy):
    """
    Base class for CofiBitStrategy supporting multiple timeframes
    taken from slack by user CofiBit
    """
    INTERFACE_VERSION: int = 3
    # Buy hyperspace params:
    buy_params = {
        "buy_fastx": 25,
        "buy_adx": 25,
    }

    # Sell hyperspace params:
    sell_params = {
        "sell_fastx": 75,
    }

    # Minimal ROI designed for the strategy.
    # This attribute will be overridden if the config file contains "minimal_roi"
    minimal_roi = {
        "40": 0.05,
        "30": 0.06,
        "20": 0.07,
        "0": 0.10
    }

    # Optimal stoploss designed for the strategy
    # This attribute will be overridden if the config file contains "stoploss"
    stoploss = -0.25

    # Timeframe will be set in subclasses
    
    # Trailing stop settings
    trailing_stop = True
    trailing_stop_positive = 0.02
    trailing_stop_positive_offset = 0.04
    trailing_only_offset_is_reached = True

    buy_fastx = IntParameter(20, 30, default=25)
    buy_adx = IntParameter(20, 30, default=25)
    sell_fastx = IntParameter(70, 80, default=75)

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        stoch_fast = ta.STOCHF(dataframe, 5, 3, 0, 3, 0)
        dataframe['fastd'] = stoch_fast['fastd']
        dataframe['fastk'] = stoch_fast['fastk']
        dataframe['ema_high'] = ta.EMA(dataframe, timeperiod=5, price='high')
        dataframe['ema_close'] = ta.EMA(dataframe, timeperiod=5, price='close')
        dataframe['ema_low'] = ta.EMA(dataframe, timeperiod=5, price='low')
        dataframe['adx'] = ta.ADX(dataframe)

        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Based on TA indicators, populates the buy signal for the given dataframe
        :param dataframe: DataFrame
        :return: DataFrame with buy column
        """
        dataframe.loc[
            (
                (dataframe['open'] < dataframe['ema_low']) &
                (qtpylib.crossed_above(dataframe['fastk'], dataframe['fastd'])) &
                (dataframe['fastk'] < self.buy_fastx.value) &
                (dataframe['fastd'] < self.buy_fastx.value) &
                (dataframe['adx'] > self.buy_adx.value)
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
                (dataframe['open'] >= dataframe['ema_high'])
            ) |
            (
                (qtpylib.crossed_above(dataframe['fastk'], self.sell_fastx.value)) |
                (qtpylib.crossed_above(dataframe['fastd'], self.sell_fastx.value))
            ),
            'exit_long'] = 1

        return dataframe


# 1分钟时间框架策略
class CofiBitStrategy1m(CofiBitStrategyBase):
    """
    CofiBitStrategy optimized for 1-minute timeframe
    """
    timeframe = '1m'
    
    # 1分钟优化的ROI设置
    minimal_roi = {
        "40": 0.03,
        "30": 0.04,
        "20": 0.05,
        "0": 0.08
    }
    
    # 1分钟优化的止损和追踪止损
    stoploss = -0.20
    trailing_stop_positive = 0.01
    trailing_stop_positive_offset = 0.025


# 5分钟时间框架策略
class CofiBitStrategy5m(CofiBitStrategyBase):
    """
    CofiBitStrategy optimized for 5-minute timeframe
    """
    timeframe = '5m'
    
    # 5分钟优化的ROI设置
    minimal_roi = {
        "40": 0.05,
        "30": 0.06,
        "20": 0.07,
        "0": 0.10
    }
    
    # 5分钟优化的止损和追踪止损
    stoploss = -0.25
    trailing_stop_positive = 0.02
    trailing_stop_positive_offset = 0.04


# 保持原有类名以向后兼容
class CofiBitStrategy(CofiBitStrategy5m):
    """
    Default CofiBitStrategy (5m timeframe for backward compatibility)
    """
    pass
