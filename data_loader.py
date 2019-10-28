from argparse import ArgumentParser
import bs4 as bs
import datetime as dt
import os
import pandas as pd
import pickle
import requests
import yfinance as yf


def get_sp500_ticker_names():
    resp = requests.get('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
    soup = bs.BeautifulSoup(resp.text, "lxml")
    table = soup.find('table', {'class': 'wikitable sortable'})
    tickers = []
    for row in table.findAll('tr')[1:]:
        ticker = row.findAll('td')[0].text[:-1].replace('.', '-')
        tickers.append(ticker)
    with open('sp500tickers.pickle', 'wb') as f:
        pickle.dump(tickers, f)

    return tickers


def load_sp500_data(args=None):
    if not os.path.exists('sp500tickers.pickle'):
        tickers = get_sp500_ticker_names()
    else:
        with open('sp500tickers.pickle', 'rb') as f:
            tickers = pickle.load(f)

    if not os.path.exists('stocks_dfs'):
        os.makedirs('stocks_dfs')

    start = dt.datetime(2000, 1, 1)
    end = dt.datetime.today()

    sp500_adj_close_df = pd.DataFrame()
    for ticker in tickers:
        if not os.path.exists(f'stocks_dfs/{ticker}.csv'):
            print(f'Installing {ticker} data')
            df = yf.download(ticker, start, end)
            df.to_csv(f'stocks_dfs/{ticker}.csv')
        else:
            df = pd.read_csv(f'stocks_dfs/{ticker}.csv', index_col=0)
        df.rename(columns={'Adj Close': ticker}, inplace=True)
        df.drop(['Open', 'High', 'Low', 'Close', 'Volume'], axis=1, inplace=True)

        if sp500_adj_close_df.empty:
            sp500_adj_close_df = df
        else:
            sp500_adj_close_df = sp500_adj_close_df.join(df, how='outer')

    sp500_adj_close_df.to_csv('sp500_joined_adj_close.csv')


if __name__ == '__main__':
    parser = ArgumentParser()
    subparsers = parser.add_subparsers()

    load_sp500_data_parser = subparsers.add_parser(
        'load_sp500_data'
        , help='''Loads sp500 stocks data(+names in sp500tickers.pickle),
                joins all by Adj Close and saves it to ./sp500_joined_adj_close.csv.'''
    )
    load_sp500_data_parser.set_defaults(func=load_sp500_data)

    args = parser.parse_args()
    args.func(args)
