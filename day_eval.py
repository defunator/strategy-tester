import datetime as dt
import numpy as np
import pandas as pd


class DayEval:
    def __init__(self
                 , start_capital
                 , frame_start
                 , frame_end
                 , adj_close_filename
                 , commission):
        self.start_capital, self.bank = start_capital, start_capital
        self.tickers_bought = {}
        self.frame_start, self.frame_end = frame_start, frame_end
        self.df = pd.read_csv(adj_close_filename, index_col=0)
        self.dates = self.df.index
        self.cur_frame = 0
        while self.cur_frame != len(self.dates) and dt.datetime.strptime(self.dates[self.cur_frame], '%Y-%m-%d') < self.frame_start:
            self.cur_frame += 1
        self.commission = commission

    def get_ticker_price(self, ticker):
        return 0 if np.isnan(self.df[ticker][self.dates[self.cur_frame]]) else self.df[ticker][self.dates[self.cur_frame]]

    def buy_ticker(self, ticker, num):
        if self.get_ticker_price(ticker) == 0 or num * self.get_ticker_price(ticker) * (1. + self.commission) > self.bank:
            return False

        if ticker not in self.tickers_bought.keys():
            self.tickers_bought[ticker] = 0
        self.tickers_bought[ticker] += num
        self.bank -= num * self.get_ticker_price(ticker) * (1. + self.commission)
        return True

    def get_ticker_num(self, ticker):
        return 0 if ticker not in self.tickers_bought.keys() else self.tickers_bought[ticker]

    def sell_ticker(self, ticker, num):
        assert ticker in self.tickers_bought.keys() and self.tickers_bought[ticker] >= num\
            , f'''ERROR sell_ticker({ticker}, {num}): not enough tickers'''
        if self.get_ticker_price(ticker) == 0:
            return False

        self.tickers_bought[ticker] -= num
        self.bank += num * self.get_ticker_price(ticker) * (1. - self.commission)
        return True

    def next_frame(self):
        if dt.datetime.strptime(self.dates[self.cur_frame], '%Y-%m-%d') >= self.frame_end \
                or self.cur_frame + 1 == len(self.dates):
            return False
        self.cur_frame += 1
        return True

    def get_profit(self):
        return self.bank - self.start_capital
