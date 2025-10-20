from freqtrade.strategy.interface import IStrategy
from pandas import DataFrame
import talib.abstract as ta


class BollingerStrategy(IStrategy):
    INTERFACE_VERSION = 3
    
    minimal_roi = {
        "0": 0.06  # 目标6%盈利（3倍于2%止损）
    }
    
    stoploss = -0.02  # 2%止损，实现小亏
    timeframe = '1h'
    
    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        bollinger = ta.BBANDS(dataframe, timeperiod=20, nbdevup=2.0, nbdevdn=2.0, matype=0)
        dataframe['bb_lower'] = bollinger['lowerband']
        dataframe['bb_middle'] = bollinger['middleband']
        dataframe['bb_upper'] = bollinger['upperband']
        
        dataframe['bb_percent'] = (dataframe['close'] - dataframe['bb_lower']) / (dataframe['bb_upper'] - dataframe['bb_lower'])
        dataframe['bb_width'] = (dataframe['bb_upper'] - dataframe['bb_lower']) / dataframe['bb_middle']
        
        dataframe['rsi'] = ta.RSI(dataframe, timeperiod=14)
        dataframe['volume_sma'] = ta.SMA(dataframe['volume'], timeperiod=20)
        
        return dataframe
    
    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        基于CYC动量效应的布林带策略：
        不在下轨买入（传统逆势），而在上轨附近追强势（顺势）
        """
        dataframe.loc[
            (
                # 价格突破布林带上轨，显示强势动量
                (dataframe['close'] > dataframe['bb_upper']) &
                # 布林带宽度适中，避免极端波动
                (dataframe['bb_width'] > 0.02) &
                (dataframe['bb_width'] < 0.15) &
                # RSI显示超强势（基于我们的发现）
                (dataframe['rsi'] > 75) &
                # 成交量放大确认突破有效性
                (dataframe['volume'] > dataframe['volume_sma'] * 1.2)
            ),
            'enter_long'] = 1
        
        return dataframe
    
    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        动量减弱时退出
        """
        dataframe.loc[
            (
                # 价格回落到布林带中轨以下
                (dataframe['close'] < dataframe['bb_middle']) |
                # RSI从高位回落
                (dataframe['rsi'] < 60)
            ),
            'exit_long'] = 1
        
        return dataframe