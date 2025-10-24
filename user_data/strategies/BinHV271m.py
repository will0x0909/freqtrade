from freqtrade.strategy import IStrategy, IntParameter, DecimalParameter, CategoricalParameter
from typing import Dict, List
from functools import reduce
from pandas import DataFrame, DatetimeIndex, merge
import talib.abstract as ta
import freqtrade.vendor.qtpylib.indicators as qtpylib
import numpy  # noqa


class BinHV271m(IStrategy):
    """
    BinHV27 strategy optimized for 1-minute timeframe
    strategy sponsored by user BinH from slack
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
    roi_p1 = DecimalParameter(0.01, 0.10, default=0.05, space="roi", optimize=True)
    roi_p2 = DecimalParameter(0.01, 0.15, default=0.10, space="roi", optimize=True)
    roi_p3 = DecimalParameter(0.01, 0.30, default=0.15, space="roi", optimize=True)
    roi_p4 = DecimalParameter(0.01, 0.50, default=0.20, space="roi", optimize=True)
    
    # Stoploss hyperopt
    stoploss_opt = DecimalParameter(-0.50, -0.01, default=-0.08, space="stoploss", optimize=True)
    
    # 1分钟优化的ROI设置
    minimal_roi = {
        "0": 0.12,
        "20": 0.08,
        "30": 0.05,
        "60": 0.02
    }
    
    # Optimal stoploss designed for the strategy
    stoploss = -0.08
    
    # Trailing stop settings
    trailing_stop = True
    trailing_stop_positive = 0.01
    trailing_stop_positive_offset = 0.025
    trailing_only_offset_is_reached = True
    
    # Number of candles the strategy requires before producing valid signals
    startup_candle_count: int = 400
    
    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe['rsi'] = numpy.nan_to_num(ta.RSI(dataframe, timeperiod=14))
        rsiframe = DataFrame(dataframe['rsi']).rename(columns={'rsi': 'close'})
        dataframe['emarsi'] = numpy.nan_to_num(ta.EMA(rsiframe, timeperiod=5))
        dataframe['adx'] = numpy.nan_to_num(ta.ADX(dataframe, timeperiod=14))
        dataframe['minusdi'] = numpy.nan_to_num(ta.MINUS_DI(dataframe, timeperiod=14))
        minusdiframe = DataFrame(dataframe['minusdi']).rename(columns={'minusdi': 'close'})
        dataframe['minusdiema'] = numpy.nan_to_num(ta.EMA(minusdiframe, timeperiod=25))
        dataframe['plusdi'] = numpy.nan_to_num(ta.PLUS_DI(dataframe, timeperiod=14))
        plusdiframe = DataFrame(dataframe['plusdi']).rename(columns={'plusdi': 'close'})
        dataframe['plusdiema'] = numpy.nan_to_num(ta.EMA(plusdiframe, timeperiod=5))
        dataframe['lowsma'] = numpy.nan_to_num(ta.EMA(dataframe, timeperiod=60))
        dataframe['highsma'] = numpy.nan_to_num(ta.EMA(dataframe, timeperiod=120))
        dataframe['fastsma'] = numpy.nan_to_num(ta.SMA(dataframe, timeperiod=120))
        dataframe['slowsma'] = numpy.nan_to_num(ta.SMA(dataframe, timeperiod=240))
        dataframe['bigup'] = dataframe['fastsma'].gt(dataframe['slowsma']) & ((dataframe['fastsma'] - dataframe['slowsma']) > dataframe['close'] / 300)
        dataframe['bigdown'] = ~dataframe['bigup']
        dataframe['trend'] = dataframe['fastsma'] - dataframe['slowsma']
        dataframe['preparechangetrend'] = dataframe['trend'].gt(dataframe['trend'].shift())
        dataframe['preparechangetrendconfirm'] = dataframe['preparechangetrend'] & dataframe['trend'].shift().gt(dataframe['trend'].shift(2))
        dataframe['continueup'] = dataframe['slowsma'].gt(dataframe['slowsma'].shift()) & dataframe['slowsma'].shift().gt(dataframe['slowsma'].shift(2))
        dataframe['delta'] = dataframe['fastsma'] - dataframe['fastsma'].shift()
        dataframe['slowingdown'] = dataframe['delta'].lt(dataframe['delta'].shift())
        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            dataframe['slowsma'].gt(0) &
            dataframe['close'].lt(dataframe['highsma']) &
            dataframe['close'].lt(dataframe['lowsma']) &
            dataframe['minusdi'].gt(dataframe['minusdiema']) &
            dataframe['rsi'].ge(dataframe['rsi'].shift()) &
            (
              (
                ~dataframe['preparechangetrend'] &
                ~dataframe['continueup'] &
                dataframe['adx'].gt(25) &
                dataframe['bigdown'] &
                dataframe['emarsi'].le(20)
              ) |
              (
                ~dataframe['preparechangetrend'] &
                dataframe['continueup'] &
                dataframe['adx'].gt(30) &
                dataframe['bigdown'] &
                dataframe['emarsi'].le(20)
              ) |
              (
                ~dataframe['continueup'] &
                dataframe['adx'].gt(35) &
                dataframe['bigup'] &
                dataframe['emarsi'].le(20)
              ) |
              (
                dataframe['continueup'] &
                dataframe['adx'].gt(30) &
                dataframe['bigup'] &
                dataframe['emarsi'].le(25)
              )
            ),
            'enter_long'] = 1
        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
              (
                ~dataframe['preparechangetrendconfirm'] &
                ~dataframe['continueup'] &
                (dataframe['close'].gt(dataframe['lowsma']) | dataframe['close'].gt(dataframe['highsma'])) &
                dataframe['highsma'].gt(0) &
                dataframe['bigdown']
              ) |
              (
                ~dataframe['preparechangetrendconfirm'] &
                ~dataframe['continueup'] &
                dataframe['close'].gt(dataframe['highsma']) &
                dataframe['highsma'].gt(0) &
                (dataframe['emarsi'].ge(75) | dataframe['close'].gt(dataframe['slowsma'])) &
                dataframe['bigdown']
              ) |
              (
                ~dataframe['preparechangetrendconfirm'] &
                dataframe['close'].gt(dataframe['highsma']) &
                dataframe['highsma'].gt(0) &
                dataframe['adx'].gt(30) &
                dataframe['emarsi'].ge(80) &
                dataframe['bigup']
              ) |
              (
                dataframe['preparechangetrendconfirm'] &
                ~dataframe['continueup'] &
                dataframe['slowingdown'] &
                dataframe['emarsi'].ge(75) &
                dataframe['slowsma'].gt(0)
              ) |
              (
                dataframe['preparechangetrendconfirm'] &
                dataframe['minusdi'].lt(dataframe['plusdi']) &
                dataframe['close'].gt(dataframe['lowsma']) &
                dataframe['slowsma'].gt(0)
              )
            ),
            'exit_long'] = 1
        return dataframe