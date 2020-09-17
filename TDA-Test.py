import requests
import datetime
import pandas as pd
import json
import bs4 as bs
import os
import pickle

key = 'INSERT YOUR OWN KEY'

# price_hist_endpoint = r'https://api.tdameritrade.com/v1/marketdata/{}/pricehistory'.format('FB')
# price_hist_endpoint = 'https://api.tdameritrade.com/v1/marketdata/FB/pricehistory'

payload = {
    'apikey': key,
    'periodType': 'year',
    # 'period': '20',
    'frequencyType': 'daily',
    'frequency': '1',
    'endDate': '1600329369000',
    'startDate': '946719000000',
    'needExtendedHoursData': 'false'
}


def list_tickers():
    with open("sp500tickers.pickle", "rb") as f:
        tickers = pickle.load(f)
    return tickers


# This scrapes the wikipedia for the SP500 using beatiful soup.
def save_sp500_tickers():
    resp = requests.get('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
    soup = bs.BeautifulSoup(resp.text, 'lxml')
    table = soup.find('table', {'class': 'wikitable sortable'})
    tickers = []
    # From the first row onward...
    for row in table.findAll('tr')[1:]:
        # Get the first element in each row.
        ticker = row.findAll('td')[0].text.replace('.', '-')
        ticker = ticker[:-1]
        tickers.append(ticker)
    # Save the sp500 tickers wb = write bits
    with open("sp500tickers.pickle", "wb") as f:
        pickle.dump(tickers, f)
    print(tickers)
    return tickers


def ret_payl():
    payload = {
        'apikey': key,
        'periodType': 'year',
        'period': '20',
        'frequencyType': 'daily',
        'frequency': '1',
        # 'endDate': '1600147228000',
        # 'startDate': '966496779000',
        'needExtendedHoursData': 'false'
    }
    return payload


def get_data_tda(reload_sp500=False):
    if reload_sp500:
        tickers = save_sp500_tickers()
    else:
        # rb = read bytes
        with open("sp500tickers.pickle", "rb") as f:
            tickers = pickle.load(f)

        # If this directory does not exist, create it.
        if not os.path.exists('stock_dfs'):
            os.makedirs('stock_dfs')

        # For each ticker, if the path does not exist for their historical data file...
        for ticker in tickers:
            print(ticker)
            if not os.path.exists('stock_dfs/{}'.format(ticker)):
                ret_payl()

            # Get the desired endpoint (ticker specific)
            endpt = format_request(ticker)

            # Request data according to parameters and endpoint.  Store response in content.
            content = requests.get(url=endpt, params=payload)

            # Convert the data to dictionary format.
            data = content.json()
            data = data['candles']

            # Dump the data
            with open('data.json', 'w') as outfile:
                json.dump(data, outfile)
            # print(data)

            df = pd.read_json('data.json')

            df.to_csv('stock_dfs/{}.csv'.format(ticker), index=False)


def format_request(ticker):
    price_hist_endpoint = r'https://api.tdameritrade.com/v1/marketdata/{}/pricehistory'.format(ticker)
    return price_hist_endpoint


if __name__ == '__main__':
    save_sp500_tickers()
    get_data_tda()


# Ideas: 
# Make command line utility to compare up to 4 stocks and their historical correlations.  (pandas has a .corr() function, should be easy)/



