from datetime import datetime
from typing import Optional

from freqtrade.strategy import IStrategy, merge_informative_pair
from pandas import DataFrame
import talib.abstract as ta
import freqtrade.vendor.qtpylib.indicators as qtpylib
import numpy  # noqa


class MACDCrossoverWithTrend(IStrategy):

    """
    MACDCrossoverWithTrend
    author@: Paul Csapak
    github@: https://github.com/paulcpk/freqtrade-strategies-that-work

    How to use it?

    > freqtrade download-data --timeframes 1h --timerange=20180301-20200301
    > freqtrade backtesting --export trades -s MACDCrossoverWithTrend --timeframe 1h --timerange=20180301-20200301
    > freqtrade plot-dataframe -s MACDCrossoverWithTrend --indicators1 ema_trend --timeframe 1h --timerange=20180301-20200301
    """

    # Minimal ROI designed for the strategy.
    # This attribute will be overridden if the config file contains "minimal_roi"
    minimal_roi = {
        "0": 0.565,
        "180": 0.12,
        "360": 0.029,
        "1620": 0
    }

    # This attribute will be overridden if the config file contains "stoploss"
    stoploss = -0.332
    can_short = True

    # Optimal timeframe for the strategy
    timeframe = '1h'

    # trailing stoploss
    use_exit_signal = False
    trailing_stop = False
    trailing_stop_positive = 0.03
    trailing_stop_positive_offset = 0.04

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:

        macd = ta.MACD(dataframe)
        dataframe['macd'] = macd['macd']
        dataframe['macdsignal'] = macd['macdsignal']
        dataframe['macdhist'] = macd['macdhist']

        dataframe['ema_trend'] = ta.EMA(dataframe, timeperiod=200)

        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:

        dataframe.loc[
            (
                    (dataframe['macd'] < 0) &  # MACD is below zero
                    # Signal crosses above MACD
                    (qtpylib.crossed_above(dataframe['macd'], dataframe['macdsignal'])) &
                    (dataframe['low'] > dataframe['ema_trend']) &  # Candle low is above EMA
                    # Ensure this candle had volume (important for backtesting)
                    (dataframe['volume'] > 0)
            ),
            'enter_long'] = 1

        dataframe.loc[
            (
                    (dataframe['macd'] > 0) &  # MACD is above zero
                    # Signal crosses below MACD
                    (qtpylib.crossed_below(dataframe['macd'], dataframe['macdsignal'])) &
                    (dataframe['high'] < dataframe['ema_trend']) &  # Candle high is below EMA
                    # Ensure this candle had volume (important for backtesting)
                    (dataframe['volume'] > 0)
            ),
            'enter_short'] = 1
        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:

        dataframe.loc[
            (
                # MACD crosses above Signal
                    (qtpylib.crossed_below(dataframe['macd'], 0)) |
                    (dataframe['low'] < dataframe['ema_trend'])  # OR price is below trend ema
            ),
            'exit_long'] = 1

        dataframe.loc[
            (
                # MACD crosses above Signal
                    (qtpylib.crossed_above(dataframe['macd'], 0)) |
                    (dataframe['high'] > dataframe['ema_trend'])  # OR price is below trend ema
            ),
            'exit_short'] = 1
        return dataframe

    def leverage(self, pair: str, current_time: datetime, current_rate: float,
                 proposed_leverage: float, max_leverage: float, entry_tag: Optional[str],
                 side: str, **kwargs) -> float:
        entry_tag = ''
        max_leverage = 1
        return max_leverage