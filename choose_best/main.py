from day_eval import DayEval
import datetime as dt
import pickle

with open('../sp500tickers.pickle', 'rb') as f:
    tickers = pickle.load(f)

max_ticker_price = 4000.
buy_step = 100

eval = DayEval(start_capital=32000
               , frame_start=dt.datetime(2017, 1, 1)
               , frame_end=dt.datetime(2018, 1, 1)
               , adj_close_filename='../sp500_joined_adj_close.csv'
               , commission=0.003)

days_cnt = 0

while True:
    if days_cnt % buy_step == 0:
        for ticker in eval.tickers_bought:
            if eval.tickers_bought[ticker] != 0:
                eval.sell_ticker(ticker, eval.tickers_bought[ticker])

        top_ticks = []
        for ticker in tickers:
            eval.cur_frame -= buy_step
            prev_price = eval.get_ticker_price(ticker)
            eval.cur_frame += buy_step
            cur_price = eval.get_ticker_price(ticker)
            if 0 in [prev_price, cur_price]:
                continue
            top_ticks.append((cur_price / prev_price, ticker))
        top_ticks.sort()

        for top_tick in top_ticks:
            ticker = top_tick[1]
            for j in range(int(max(1., max_ticker_price / float(eval.get_ticker_price(ticker))))):
                eval.buy_ticker(ticker, 1)

    days_cnt += 1
    if not eval.next_frame():
        break

for ticker in eval.tickers_bought:
    if eval.tickers_bought[ticker] != 0:
        eval.sell_ticker(ticker, eval.tickers_bought[ticker])

print(eval.bank / eval.start_capital)

