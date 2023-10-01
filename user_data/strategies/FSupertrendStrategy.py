"""
Supertrend strategy:
* Description: Generate a 3 supertrend indicators for 'buy' strategies & 3 supertrend indicators for 'sell' strategies
               Buys if the 3 'buy' indicators are 'up'
               Sells if the 3 'sell' indicators are 'down'
* Author: @juankysoriano (Juan Carlos Soriano)
* github: https://github.com/juankysoriano/
*** NOTE: This Supertrend strategy is just one of many possible strategies using `Supertrend` as indicator. It should on any case used at your own risk.
          It comes with at least a couple of caveats:
            1. The implementation for the `supertrend` indicator is based on the following discussion: https://github.com/freqtrade/freqtrade-strategies/issues/30 . Concretelly https://github.com/freqtrade/freqtrade-strategies/issues/30#issuecomment-853042401
            2. The implementation for `supertrend` on this strategy is not validated; meaning this that is not proven to match the results by the paper where it was originally introduced or any other trusted academic resources
"""

import logging
from numpy.lib import math
from freqtrade.strategy import IStrategy, IntParameter
from pandas import DataFrame
import pandas_ta as ta
import numpy as np

import talib.abstract as ta
import freqtrade.vendor.qtpylib.indicators as qtpylib


class FSupertrendStrategy(IStrategy):
    # Buy params, Sell params, ROI, Stoploss and Trailing Stop are values generated by 'freqtrade hyperopt --strategy Supertrend --hyperopt-loss ShortTradeDurHyperOptLoss --timerange=20210101- --timeframe=1h --spaces all'
    # It's encourage you find the values that better suites your needs and risk management strategies

    INTERFACE_VERSION: int = 3
    # Buy hyperspace params:
    buy_params = {
        "buy_ema": 200,
        # "buy_m1": 1,
        # "buy_m2": 2,
        # "buy_m3": 3,
        # "buy_p1": 10,
        # "buy_p2": 11,
        # "buy_p3": 12,
    }

    # Sell hyperspace params:
    sell_params = {
        "sell_ema": 200,
        # "sell_m1": 1,
        # "sell_m2": 2,
        # "sell_m3": 3,
        # "sell_p1": 10,
        # "sell_p2": 11,
        # "sell_p3": 12,
    }

    # ROI table:
    minimal_roi = {"0": 0.1, "30": 0.75, "60": 0.05, "120": 0.025}
    # minimal_roi = {"0": 0.01, "30": 0.075, "60": 0.005, "120": 0.0025}  #5m
    # minimal_roi = {"0": 1}

    # Stoploss:
    stoploss = -0.265
    can_short = True

    # Trailing stop:
    trailing_stop = True
    trailing_stop_positive = 0.05
    trailing_stop_positive_offset = 0.1
    trailing_only_offset_is_reached = False

    timeframe = "1h"

    startup_candle_count = 18

    buy_ema = IntParameter(190, 210, default=200, space="buy")
    # buy_m1 = IntParameter(1, 4, default=1)
    # buy_m2 = IntParameter(1, 4, default=2)
    # buy_m3 = IntParameter(1, 4, default=3)
    # buy_p1 = IntParameter(9, 15, default=10)
    # buy_p2 = IntParameter(9, 15, default=11)
    # buy_p3 = IntParameter(9, 15, default=12)

    sell_ema = IntParameter(190, 210, default=200, space="sell")

    # sell_m1 = IntParameter(1, 4, default=1)
    # sell_m2 = IntParameter(1, 4, default=2)
    # sell_m3 = IntParameter(1, 4, default=3)
    # sell_p1 = IntParameter(9, 15, default=10)
    # sell_p2 = IntParameter(9, 15, default=11)
    # sell_p3 = IntParameter(9, 15, default=12)

    plot_config = {
        'main_plot': {
            'supertrend1': {},
            'supertrend2': {},
            'supertrend3': {},
            'sell_ema_200': {'color': 'blue'},
            'ema21': {'color': 'white'},
        }
    }

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # for multiplier in self.buy_m1.range:
        #     for period in self.buy_p1.range:
        #         dataframe[f"supertrend_1_buy_{multiplier}_{period}"] = self.supertrend(
        #             dataframe, multiplier, period
        #         )["STX"]
        #
        # for multiplier in self.buy_m2.range:
        #     for period in self.buy_p2.range:
        #         dataframe[f"supertrend_2_buy_{multiplier}_{period}"] = self.supertrend(
        #             dataframe, multiplier, period
        #         )["STX"]
        #
        # for multiplier in self.buy_m3.range:
        #     for period in self.buy_p3.range:
        #         dataframe[f"supertrend_3_buy_{multiplier}_{period}"] = self.supertrend(
        #             dataframe, multiplier, period
        #         )["STX"]
        #
        # for multiplier in self.sell_m1.range:
        #     for period in self.sell_p1.range:
        #         dataframe[f"supertrend_1_sell_{multiplier}_{period}"] = self.supertrend(
        #             dataframe, multiplier, period
        #         )["STX"]
        #
        # for multiplier in self.sell_m2.range:
        #     for period in self.sell_p2.range:
        #         dataframe[f"supertrend_2_sell_{multiplier}_{period}"] = self.supertrend(
        #             dataframe, multiplier, period
        #         )["STX"]
        #
        # for multiplier in self.sell_m3.range:
        #     for period in self.sell_p3.range:
        #         dataframe[f"supertrend_3_sell_{multiplier}_{period}"] = self.supertrend(
        #             dataframe, multiplier, period
        #         )["STX"]

        # dataframe["supertrend1"] = self.supertrend(dataframe, 1, 10)["STX"]
        # dataframe["supertrend2"] = self.supertrend(dataframe, 2, 11)["STX"]
        # dataframe["supertrend3"] = self.supertrend(dataframe, 3, 12)["STX"]

        dataframe.ta.supertrend(period=10, multiplier=1, append=True)
        dataframe.ta.supertrend(period=11, multiplier=2, append=True)
        dataframe.ta.supertrend(period=12, multiplier=3, append=True)

        for period in self.buy_ema.range:
            dataframe[f"sell_ema_{period}"] = ta.EMA(dataframe, timeperiod=period)

        for period in self.sell_ema.range:
            dataframe[f"sell_ema_{period}"] = ta.EMA(dataframe, timeperiod=period)

        dataframe["adx"] = ta.ADX(dataframe)
        dataframe["plus_di"] = ta.PLUS_DI(dataframe)
        dataframe["minus_di"] = ta.MINUS_DI(dataframe)
        dataframe["ema21"] = ta.EMA(dataframe, timeperiod=28)

        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:

        dataframe.loc[
            (dataframe[f"sell_ema_{self.buy_ema.value}"] < dataframe["close"])
            & (dataframe[f"sell_ema_{self.buy_ema.value}"].shift(1) < dataframe["close"].shift(1))
            & (dataframe["ema21"] < dataframe["close"])
            & (dataframe["SUPERTd_7_1.0"] == 1)
            & (dataframe["SUPERTd_7_2.0"] == 1)
            & (dataframe["SUPERTd_7_3.0"] == 1)
            & (dataframe["volume"] > 0),
            "enter_long",
        ] = 1

        dataframe.loc[
            (dataframe[f"sell_ema_{self.sell_ema.value}"] > dataframe["close"])
            & (dataframe[f"sell_ema_{self.buy_ema.value}"].shift(1) > dataframe["close"].shift(1))
            & (dataframe["ema21"] > dataframe["close"])
            & (dataframe["SUPERTd_7_1.0"] == -1)
            & (dataframe["SUPERTd_7_2.0"] == -1)
            & (dataframe["SUPERTd_7_3.0"] == -1)
            & (dataframe["volume"] > 0),
            "enter_short",
        ] = 1

        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            # (dataframe["supertrend1"] == "down")
            # | (dataframe["supertrend2"] == "down")
            # | (dataframe["supertrend3"] == "down")
            # |
            (qtpylib.crossed_above(dataframe["adx"], dataframe["plus_di"])),
            "exit_long",
        ] = 1

        dataframe.loc[
            # (dataframe["supertrend1"] == "up")
            # | (dataframe["supertrend2"] == "up")
            # | (dataframe["supertrend3"] == "up")
            # |
            (qtpylib.crossed_below(dataframe["adx"], dataframe["minus_di"])),
            "exit_short",
        ] = 1

        return dataframe

    """
        Supertrend Indicator; adapted for freqtrade
        from: https://github.com/freqtrade/freqtrade-strategies/issues/30
    """

    def supertrend(self, dataframe: DataFrame, multiplier, period):
        df = dataframe.copy()

        df["TR"] = ta.TRANGE(df)
        df["ATR"] = ta.SMA(df["TR"], period)

        st = "ST_" + str(period) + "_" + str(multiplier)
        stx = "STX_" + str(period) + "_" + str(multiplier)

        # Compute basic upper and lower bands
        df["basic_ub"] = (df["high"] + df["low"]) / 2 + multiplier * df["ATR"]
        df["basic_lb"] = (df["high"] + df["low"]) / 2 - multiplier * df["ATR"]

        # Compute final upper and lower bands
        df["final_ub"] = 0.00
        df["final_lb"] = 0.00
        for i in range(period, len(df)):
            df["final_ub"].iat[i] = (
                df["basic_ub"].iat[i]
                if df["basic_ub"].iat[i] < df["final_ub"].iat[i - 1]
                   or df["close"].iat[i - 1] > df["final_ub"].iat[i - 1]
                else df["final_ub"].iat[i - 1]
            )
            df["final_lb"].iat[i] = (
                df["basic_lb"].iat[i]
                if df["basic_lb"].iat[i] > df["final_lb"].iat[i - 1]
                   or df["close"].iat[i - 1] < df["final_lb"].iat[i - 1]
                else df["final_lb"].iat[i - 1]
            )

        # Set the Supertrend value
        df[st] = 0.00
        for i in range(period, len(df)):
            df[st].iat[i] = (
                df["final_ub"].iat[i]
                if df[st].iat[i - 1] == df["final_ub"].iat[i - 1]
                   and df["close"].iat[i] <= df["final_ub"].iat[i]
                else df["final_lb"].iat[i]
                if df[st].iat[i - 1] == df["final_ub"].iat[i - 1]
                   and df["close"].iat[i] > df["final_ub"].iat[i]
                else df["final_lb"].iat[i]
                if df[st].iat[i - 1] == df["final_lb"].iat[i - 1]
                   and df["close"].iat[i] >= df["final_lb"].iat[i]
                else df["final_ub"].iat[i]
                if df[st].iat[i - 1] == df["final_lb"].iat[i - 1]
                   and df["close"].iat[i] < df["final_lb"].iat[i]
                else 0.00
            )
        # Mark the trend direction up/down
        df[stx] = np.where(
            (df[st] > 0.00), np.where((df["close"] < df[st]), "down", "up"), np.NaN
        )

        # Remove basic and final bands from the columns
        df.drop(["basic_ub", "basic_lb", "final_ub", "final_lb"], inplace=True, axis=1)

        df.fillna(0, inplace=True)

        return DataFrame(index=df.index, data={"ST": df[st], "STX": df[stx]})
