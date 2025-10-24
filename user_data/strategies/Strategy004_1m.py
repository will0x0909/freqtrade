# --- Do not remove these libs ---
from freqtrade.strategy import IStrategy, DecimalParameter, IntParameter
from typing import Dict, List
from functools import reduce
from pandas import DataFrame
# --------------------------------

import talib.abstract as ta


class Strategy004_1m(IStrategy):
    """
    Strategy004 optimized for 1-minute timeframe
    author@: Gerald Lonlas
    github@: https://github.com/freqtrade/freqtrade-strategies
    """
    INTERFACE_VERSION: int = 3
    
    # Timeframe for this strategy
    timeframe = '1m'
    
    # Hyperopt parameters for buy signals
    buy_adx = IntParameter(20, 80, default=50, space='buy', optimize=True)
    buy_slowadx = IntParameter(15, 40, default=26, space='buy', optimize=True) 
    buy_cci = IntParameter(-200, -50, default=-100, space='buy', optimize=True)
    buy_fastk_th = IntParameter(10, 30, default=20, space='buy', optimize=True)
    buy_fastd_th = IntParameter(10, 30, default=20, space='buy', optimize=True)
    buy_slowfastk_th = IntParameter(20, 40, default=30, space='buy', optimize=True)
    buy_slowfastd_th = IntParameter(20, 40, default=30, space='buy', optimize=True)
    buy_volume_th = DecimalParameter(0.5, 1.5, default=0.75, space='buy', optimize=True)
    
    # Hyperopt parameters for sell signals
    sell_slowadx = IntParameter(15, 35, default=25, space='sell', optimize=True)
    sell_fastk_th = IntParameter(60, 90, default=70, space='sell', optimize=True)
    sell_fastd_th = IntParameter(60, 90, default=70, space='sell', optimize=True)
    
    # ROI optimization parameters
    roi_t1 = IntParameter(10, 120, default=60, space="roi", optimize=True)
    roi_t2 = IntParameter(10, 60, default=30, space="roi", optimize=True)  
    roi_t3 = IntParameter(5, 40, default=20, space="roi", optimize=True)
    roi_p1 = DecimalParameter(0.01, 0.30, default=0.10, space="roi", optimize=True)
    roi_p2 = DecimalParameter(0.01, 0.50, default=0.30, space="roi", optimize=True)
    roi_p3 = DecimalParameter(0.01, 0.70, default=0.40, space="roi", optimize=True)
    roi_p4 = DecimalParameter(0.01, 1.00, default=0.50, space="roi", optimize=True)
    
    # Stoploss optimization
    stoploss_opt = DecimalParameter(-0.50, -0.05, default=-0.20, space="stoploss", optimize=True)
    
    # Trailing stop optimization  
    trailing_stop_positive_opt = DecimalParameter(0.005, 0.05, default=0.005, space="stoploss", optimize=True)
    trailing_stop_positive_offset_opt = DecimalParameter(0.01, 0.10, default=0.015, space="stoploss", optimize=True)
    
    # Default values (will be optimized by hyperopt) - 1m optimized
    minimal_roi = {
        "0": 0.5,
        "20": 0.4,
        "30": 0.3,
        "60": 0.1
    }
    
    stoploss = -0.20
    trailing_stop_positive = 0.005
    trailing_stop_positive_offset = 0.015
    
    # Buy hyperspace params
    buy_params = {
        "buy_adx": 50,
        "buy_slowadx": 26,
        "buy_cci": -100,
        "buy_fastk_th": 20,
        "buy_fastd_th": 20,
        "buy_slowfastk_th": 30,
        "buy_slowfastd_th": 30,
        "buy_volume_th": 0.75,
    }
    
    # Sell hyperspace params
    sell_params = {
        "sell_slowadx": 25,
        "sell_fastk_th": 70,
        "sell_fastd_th": 70,
    }

    # trailing stoploss
    trailing_stop = True

    # run "populate_indicators" only for new candle
    process_only_new_candles = True

    # Experimental settings (configuration will overide these if set)
    use_exit_signal = True
    exit_profit_only = True
    ignore_roi_if_entry_signal = False

    # Optional order type mapping
    order_types = {
        'entry': 'limit',
        'exit': 'limit',
        'stoploss': 'market',
        'stoploss_on_exchange': False
    }

    def informative_pairs(self):
        """
        Define additional, informative pair/interval combinations to be cached from the exchange.
        These pair/interval combinations are non-tradeable, unless they are part
        of the whitelist as well.
        For more information, please consult the documentation
        :return: List of tuples in the format (pair, interval)
            Sample: return [("ETH/USDT", "5m"),
                            ("BTC/USDT", "15m"),
                            ]
        """
        return []

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Adds several different TA indicators to the given DataFrame

        Performance Note: For the best performance be frugal on the number of indicators
        you are using. Let uncomment only the indicator you are using in your strategies
        or your hyperopt configuration, otherwise you will waste your memory and CPU usage.
        """

        # ADX
        dataframe['adx'] = ta.ADX(dataframe)
        dataframe['slowadx'] = ta.ADX(dataframe)

        # Commodity Channel Index: values Oversold:<-100, Overbought:>100
        dataframe['cci'] = ta.CCI(dataframe)

        # Stoch
        stoch = ta.STOCHF(dataframe)
        dataframe['fastd'] = stoch['fastd']
        dataframe['fastk'] = stoch['fastk']
        dataframe['fastk-previous'] = dataframe.fastk.shift(1)
        dataframe['fastd-previous'] = dataframe.fastd.shift(1)

        # Slow Stoch
        slowstoch = ta.STOCHF(dataframe)
        dataframe['slowfastd'] = slowstoch['fastd']
        dataframe['slowfastk'] = slowstoch['fastk']
        dataframe['slowfastk-previous'] = dataframe.slowfastk.shift(1)
        dataframe['slowfastd-previous'] = dataframe.slowfastd.shift(1)

        # EMA - Exponential Moving Average
        dataframe['ema5'] = ta.EMA(dataframe)
        
        # get the rolling volume mean for the last hour (60x1m)
        # Note: dataframe['volume'].mean() uses the whole dataframe in 
        # backtesting hence will have lookahead, but would be fine for dry/live use
        dataframe['mean-volume'] = dataframe['volume'].rolling(60).mean()

        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Based on TA indicators, populates the buy signal for the given dataframe
        :param dataframe: DataFrame
        :return: DataFrame with buy column
        """
        dataframe.loc[
            (
                (
                    (dataframe['adx'] > self.buy_adx.value) |
                    (dataframe['slowadx'] > self.buy_slowadx.value)
                ) &
                (dataframe['cci'] < self.buy_cci.value) &
                (
                    (dataframe['fastk-previous'] < self.buy_fastk_th.value) &
                    (dataframe['fastd-previous'] < self.buy_fastd_th.value)
                ) &
                (
                    (dataframe['slowfastk-previous'] < self.buy_slowfastk_th.value) &
                    (dataframe['slowfastd-previous'] < self.buy_slowfastd_th.value)
                ) &
                (dataframe['fastk-previous'] < dataframe['fastd-previous']) &
                (dataframe['fastk'] > dataframe['fastd']) &
                (dataframe['mean-volume'] > self.buy_volume_th.value) &
                (dataframe['close'] > 0.00000100)
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
                (dataframe['slowadx'] < self.sell_slowadx.value) &
                ((dataframe['fastk'] > self.sell_fastk_th.value) | (dataframe['fastd'] > self.sell_fastd_th.value)) &
                (dataframe['fastk-previous'] < dataframe['fastd-previous']) &
                (dataframe['close'] > dataframe['ema5'])
            ),
            'exit_long'] = 1
        return dataframe