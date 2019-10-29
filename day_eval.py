import pandas as pd
import numpy as np


class DayEval:
    def __init__(self
                 , start_capital
                 , frame_start
                 , frame_end
                 , frame_step
                 , adj_close_filename
                 , commission):
        self.start_capital, self.bank = start_capital, start_capital
        self.tickers_bought = {}
        self.frame_start, self.frame_end = frame_start, frame_end
        self.frame_step = frame_step
        self.cur_frame = frame_start
        self.df = pd.read_csv(adj_close_filename, index_col=0)
        self.commission = commission

    def get_ticker_price(self, ticker):
        return 0 if self.cur_frame.strftime('%Y-%m-%d') not in self.df[ticker] or np.isnan(self.df[ticker][self.cur_frame.strftime('%Y-%m-%d')])\
            else self.df[ticker][self.cur_frame.strftime('%Y-%m-%d')]

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
        assert ticker in self.tickers_bought.keys() and self.tickers_bought[ticker] >= num \
            , f'''ERROR sell_ticker({ticker}, {num}): not enough tickers'''
        if self.get_ticker_price(ticker) == 0:
            return False

        self.tickers_bought[ticker] -= num
        self.bank += num * self.get_ticker_price(ticker) * (1. - self.commission)
        return True

    def next_frame(self):
        if self.cur_frame >= self.frame_end:
            return False
        self.cur_frame += self.frame_step
        return True

    def get_profit(self):
        return self.bank - self.start_capital
