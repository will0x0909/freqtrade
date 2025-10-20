from freqtrade.strategy.interface import IStrategy
from pandas import DataFrame
import talib.abstract as ta


class EMAStrategy(IStrategy):
    INTERFACE_VERSION = 3
    
    minimal_roi = {
        "60": 0.01,
        "30": 0.025,
        "0": 0.05
    }
    
    stoploss = -0.09
    timeframe = '1h'
    
    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe['ema_12'] = ta.EMA(dataframe, timeperiod=12)
        dataframe['ema_26'] = ta.EMA(dataframe, timeperiod=26)
        dataframe['ema_50'] = ta.EMA(dataframe, timeperiod=50)
        
        dataframe['ema_crossover'] = dataframe['ema_12'] > dataframe['ema_26']
        dataframe['ema_trend'] = dataframe['ema_26'] > dataframe['ema_50']
        
        dataframe['adx'] = ta.ADX(dataframe, timeperiod=14)
        dataframe['volume_sma'] = ta.SMA(dataframe['volume'], timeperiod=20)
        
        return dataframe
    
    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
                (dataframe['ema_crossover'] == True) &
                (dataframe['ema_crossover'].shift(1) == False) &
                (dataframe['ema_trend'] == True) &
                (dataframe['close'] > dataframe['ema_12']) &
                (dataframe['adx'] > 25) &
                (dataframe['volume'] > dataframe['volume_sma'])
            ),
            'enter_long'] = 1
        
        return dataframe
    
    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
                (dataframe['ema_crossover'] == False) &
                (dataframe['ema_crossover'].shift(1) == True)
            ),
            'exit_long'] = 1
        
        return dataframe