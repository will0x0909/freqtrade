from freqtrade.strategy.interface import IStrategy
from pandas import DataFrame
import talib.abstract as ta


class StochATRStrategy(IStrategy):
    INTERFACE_VERSION = 3
    
    minimal_roi = {
        "60": 0.015,
        "30": 0.03,
        "0": 0.06
    }
    
    stoploss = -0.08
    timeframe = '1h'
    
    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        stoch = ta.STOCH(dataframe, fastk_period=14, slowk_period=3, slowd_period=3)
        dataframe['stoch_k'] = stoch['slowk']
        dataframe['stoch_d'] = stoch['slowd']
        
        dataframe['atr'] = ta.ATR(dataframe, timeperiod=14)
        dataframe['atr_ma'] = ta.SMA(dataframe['atr'], timeperiod=10)
        
        dataframe['ema_21'] = ta.EMA(dataframe, timeperiod=21)
        dataframe['volume_sma'] = ta.SMA(dataframe['volume'], timeperiod=20)
        
        dataframe['volatility_filter'] = dataframe['atr'] > dataframe['atr_ma']
        
        return dataframe
    
    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
                (dataframe['stoch_k'] < 20) &
                (dataframe['stoch_d'] < 20) &
                (dataframe['stoch_k'] > dataframe['stoch_d']) &
                (dataframe['stoch_k'].shift(1) <= dataframe['stoch_d'].shift(1)) &
                (dataframe['close'] > dataframe['ema_21']) &
                (dataframe['volatility_filter'] == True) &
                (dataframe['volume'] > dataframe['volume_sma'])
            ),
            'enter_long'] = 1
        
        return dataframe
    
    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
                (dataframe['stoch_k'] > 80) &
                (dataframe['stoch_d'] > 80) &
                (dataframe['stoch_k'] < dataframe['stoch_d'])
            ),
            'exit_long'] = 1
        
        return dataframe