from day_eval import DayEval
import datetime as dt
import pickle
from random import choice

with open('../sp500tickers.pickle', 'rb') as f:
    tickers = pickle.load(f)

max_ticker_price = 10000.
buy_step = 20
upper_ratio = 1.2
lower_ratio = 0.8

mean_res_ratio = 0
test_num = 10

for test in range(test_num):
    eval = DayEval(start_capital=200000
                   , frame_start=dt.datetime(2017, 1, 1)
                   , frame_end=dt.datetime(2018, 1, 1)
                   , frame_step=dt.timedelta(days=1)
                   , adj_close_filename='../sp500_joined_adj_close.csv'
                   , commission=0.003)

    days_cnt = 0
    prices = {}

    while True:
        for ticker in prices:
            prcs = prices[ticker]
            new_prcs = []
            for prc in prcs:
                if (eval.get_ticker_price(ticker) / prc > upper_ratio or eval.get_ticker_price(ticker) / prc < lower_ratio) and eval.sell_ticker(ticker, 1):
                    pass
                else:
                    new_prcs.append(prc)
            prices[ticker] = new_prcs

        if days_cnt % buy_step == 0:
            for i in range(1):
                ticker = choice(tickers)
                if eval.get_ticker_price(ticker) > max_ticker_price or eval.get_ticker_price(ticker) == 0:
                    continue
                if ticker not in prices.keys():
                    prices[ticker] = []

                for j in range(int(max(1., max_ticker_price / float(eval.get_ticker_price(ticker))))):
                    if eval.buy_ticker(ticker, 1):
                        prices[ticker].append(eval.get_ticker_price(ticker))

        days_cnt += 1
        if not eval.next_frame():
            break

    for i in range(10):
        for ticker in eval.tickers_bought:
            if eval.tickers_bought[ticker] != 0:
                eval.sell_ticker(ticker, eval.tickers_bought[ticker])
        eval.cur_frame += eval.frame_step

    print(eval.bank / eval.start_capital)
    mean_res_ratio += eval.bank / eval.start_capital

mean_res_ratio /= test_num
print(mean_res_ratio)
