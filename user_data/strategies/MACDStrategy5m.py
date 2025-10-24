# --- Do not remove these libs ---
from freqtrade.strategy import IStrategy
from freqtrade.strategy import CategoricalParameter, DecimalParameter, IntParameter
from pandas import DataFrame
# --------------------------------

import talib.abstract as ta


class MACDStrategy5m(IStrategy):
    """
    MACDStrategy optimized for 5-minute timeframe
    author@: Gert Wohlgemuth

    idea:
        uptrend definition: MACD above MACD signal and CCI < -50
        downtrend definition: MACD below MACD signal and CCI > 100
    """
    INTERFACE_VERSION: int = 3
    
    # Timeframe for this strategy
    timeframe = '5m'

    # Minimal ROI designed for the strategy (5m optimized)
    minimal_roi = {
        "0": 0.119,
        "39": 0.047,
        "92": 0.018,
        "167": 0
    }

    # Optimal stoploss designed for the strategy
    stoploss = -0.206
    
    # Trailing stop settings
    trailing_stop = True
    trailing_stop_positive = 0.02  # Start trailing when profit is 2%
    trailing_stop_positive_offset = 0.04  # Trail 4% below high
    trailing_only_offset_is_reached = True

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