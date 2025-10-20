from freqtrade.strategy.interface import IStrategy
from pandas import DataFrame
import talib.abstract as ta


class MACDStrategy(IStrategy):
    INTERFACE_VERSION = 3
    
    minimal_roi = {
        "60": 0.01,
        "30": 0.025,
        "0": 0.05
    }
    
    stoploss = -0.08
    timeframe = '1h'
    
    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        macd = ta.MACD(dataframe, fastperiod=12, slowperiod=26, signalperiod=9)
        dataframe['macd'] = macd['macd']
        dataframe['macdsignal'] = macd['macdsignal']
        dataframe['macdhist'] = macd['macdhist']
        
        dataframe['ema_20'] = ta.EMA(dataframe, timeperiod=20)
        dataframe['volume_sma'] = ta.SMA(dataframe['volume'], timeperiod=20)
        
        return dataframe
    
    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
                (dataframe['macd'] > dataframe['macdsignal']) &
                (dataframe['macdhist'] > 0) &
                (dataframe['close'] > dataframe['ema_20']) &
                (dataframe['volume'] > dataframe['volume_sma'])
            ),
            'enter_long'] = 1
        
        return dataframe
    
    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
                (dataframe['macd'] < dataframe['macdsignal']) &
                (dataframe['macdhist'] < 0)
            ),
            'exit_long'] = 1
        
        return dataframe