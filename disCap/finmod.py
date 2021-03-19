import json
import pandas as pd
from urllib.request import urlopen
import datetime
import numpy as np
import datetime
import os

'''
get_jsonparsed_data is copied directly from https://financialmodelingprep.com.
This is the main call to process the variable url's to the API
'''
def get_jsonparsed_data(url):
    """
    Receive the content of ``url``, parse it as JSON and return the object.

    Parameters
    ----------
    url : str

    Returns
    -------
    dict
    """
    response = urlopen(url)
    data = response.read().decode("utf-8")
    return json.loads(data)


def get_current_metrics(symbol, api_key):
    prefix = 'https://financialmodelingprep.com/api/v3/profile/'
    url = '{}{}?apikey={}'.format(prefix,symbol, api_key)
    result = get_jsonparsed_data(url)
    return result

def get_historic_data(symbol, api_key):
    def extract_history(result):
        datestamp =[]
        close = []
        high = []
        low = []
        volume = []
        for token in result['historical']:
            datestamp.append(token['date'])
            close.append(token['close'])
            high.append(token['high'])
            low.append(token['low'])
            volume.append(token['volume'])
        df = pd.DataFrame.from_dict({ 'symbol':symbol, 'datestamp':datestamp, 'close':close,
                                       'high':high, 'low':low, 'volume':volume})
        return df

    prefix = 'https://financialmodelingprep.com/api/v3/historical-price-full/'
    url = '{}{}?apikey={}'.format(prefix, symbol, api_key)
    result = get_jsonparsed_data(url)
    return extract_history(result)

def get_current_metrics(symbol, api_key):
    prefix = 'https://financialmodelingprep.com/api/v3/profile/'
    url = '{}{}?apikey={}'.format(prefix,symbol, api_key)
    result = get_jsonparsed_data(url)
    return result


def check4archived_data(symbol):
    tdy = datetime.datetime.now().strftime("%Y%m%d")
    arc = 'data/arc/{}'.format(tdy)
    if not os.path.isdir(arc):
        os.mkdir(arc)
        return False, None
    filename = '{}/{}.json'.format(arc,symbol)
    if os.path.isfile(filename):
        print('Pulling data from {} for today: {}'.format(filename,symbol))
        with open(filename, 'r') as stock_historic:
            result = json.load(stock_historic)
            return True, result
    else:
        return False, None
    return False, None


def get_historic_data(symbol, api_key):
    def extract_history(result):
        datestamp =[]
        close = []
        high = []
        low = []
        volume = []
        for token in result['historical']:
            datestamp.append(token['date'])
            close.append(token['close'])
            high.append(token['high'])
            low.append(token['low'])
            volume.append(token['volume'])
        df = pd.DataFrame.from_dict({ 'symbol':symbol, 'datestamp':datestamp, 'close':close,
                                       'high':high, 'low':low, 'volume':volume})
        return df

    # check if this has been done already today
    status, result = check4archived_data(symbol)
    if status is False:
        print('Reading {} and writing to archive'.format(symbol))
        prefix = 'https://financialmodelingprep.com/api/v3/historical-price-full/'
        url = '{}{}?apikey={}'.format(prefix, symbol, api_key)
        result = get_jsonparsed_data(url)
        tdy = datetime.datetime.now().strftime("%Y%m%d")
        arc = 'data/arc/{}'.format(tdy)
        filename = '{}/{}.json'.format(arc,symbol)
        with open(filename, 'w') as outfile:
            json.dump(result, outfile)

    print('Symbol: {}.  Keys: {}'.format(symbol, result.keys()))
    try:
        print(result['Error Message'])
    except:
        print('continue...\n')
    return extract_history(result)

def get_datestamp_past(datestamp, days_ago):
    ref_date = datetime.datetime.strptime(datestamp, "%Y-%m-%d")
    past_date = ref_date - datetime.timedelta(days_ago)
    past_datestamp = datetime.datetime.strftime(past_date, "%Y-%m-%d")
    return past_datestamp

assert '2020-06-16' == get_datestamp_past('2020-06-17', 1)
assert '2020-09-07' == get_datestamp_past('2021-03-06', 180)

def findwindowave(values, window):
    mx = len(values)
    windowave = []
    for k in range(0,mx):
        right = min( mx, k+window+1 )
        left = max( 0, (k - window) )
        v = values[left:right]
        windowave.append( np.median( v ) )
    return windowave

values = [239.0,
          239.1,
          255.2,
          269.3,
          273.4,
          259.5,
          253.6,
          266.7,
          285.8,
          265.9]
window = 2
averages = findwindowave(values, window)

assert [239.1, 247.14999999999998, 255.2, 259.5, 259.5, 266.7, 266.7, 265.9, 266.29999999999995, 266.7] == averages


def get_maxmedian_pastdays(df, mostrecent_day, earliest_day, window):
    datestamp = max(df['datestamp'])
    mostrecent_datestamp = get_datestamp_past(datestamp, mostrecent_day)
    earliest_datestamp = get_datestamp_past(datestamp, earliest_day)
    closes = df[(\
                 (df.datestamp<=mostrecent_datestamp) & (df.datestamp>earliest_datestamp) \
                )\
               ]['close']
    values = findwindowave(closes, window)
    past_maxmediandays = max(values)
    return past_maxmediandays

def calc_metrics(df):
    df = df.sort_values(by=['datestamp'], ascending=False)
    x = list( df['close'].head(2) )
    last_close, prev_close = x[0], x[1]

    window, mostrecent_day, earliest_day = 5, 120, 240
    maxmed240 = get_maxmedian_pastdays(df, mostrecent_day, earliest_day, window)

    window, mostrecent_day, earliest_day = 5, 60, 120
    maxmed120 = get_maxmedian_pastdays(df, mostrecent_day, earliest_day, window)

    window, mostrecent_day, earliest_day = 5, 30, 60
    maxmed60 = get_maxmedian_pastdays(df, mostrecent_day, earliest_day, window)

    window, mostrecent_day, earliest_day = 5, 10, 30
    maxmed30 = get_maxmedian_pastdays(df, mostrecent_day, earliest_day, window)

    window, mostrecent_day, earliest_day = 5, 1, 10
    maxmed10 = get_maxmedian_pastdays(df, mostrecent_day, earliest_day, window)

    return [last_close, prev_close, maxmed10, maxmed30, maxmed60, maxmed120, maxmed240]

def get_data(symbol, api_key):
    df = get_historic_data(symbol, api_key)
    v = calc_metrics(df)
    return (symbol, v[0], v[1], v[2], v[3], v[4], v[5], v[6])


def portfolio_data(symbols, api_key):
    current_data = map( get_data, symbols, [api_key]*len(symbols) )

    symbol = []
    close = []
    prev_close = []
    maxmed10 = []
    maxmed30 = []
    maxmed60 = []
    maxmed120 = []
    maxmed240 = []

    current_data = list(current_data)

    for c in current_data:
        symbol.append(c[0])
        close.append(c[1])
        prev_close.append(c[2])
        maxmed10.append(c[3])
        maxmed30.append(c[4])
        maxmed60.append(c[5])
        maxmed120.append(c[6])
        maxmed240.append(c[7])

    dfx = pd.DataFrame.from_dict({
            'symbol':symbol,
            'close':close,
            'prev_close':prev_close,
            'maxmed10': maxmed10,
            'maxmed30': maxmed30,
            'maxmed60': maxmed60,
            'maxmed120': maxmed120,
            'maxmed240': maxmed240 })

    return dfx


def investmentsAs_df(investments):
    def cnvrtdt(datestring):
        return datetime.strptime(datestring, "%Y.%m.%d")
    def getage(dt):
        now = datetime.now()
        return (now - dt).days
    keys = investments.keys()
    keydates = []
    shares = []
    invested = []
    symbol = []
    datestamp = []

    for key in keys:
        invest_list = investments[key]
        for v in investments[key]:
            keydates.append('{}:{}'.format(key,v[0]))
            datestamp.append(v[0])
            invested.append(v[1])
            shares.append(v[2])
            symbol.append(key)

    dfx = pd.DataFrame.from_dict({
            'keydates':keydates,
            'symbol':symbol,
            'datestamp':datestamp,
            'invested':invested,
            'shares':shares
                            })

    df0 = dfx[['symbol','invested','shares']].groupby('symbol').agg('sum').reset_index()
    df1 = dfx[['symbol','datestamp']].groupby('symbol').agg('min').reset_index()

    df2 = df1.merge(df0, how='left', on='symbol')
    df1 = df2.rename(columns={"datestamp": "first_investment"})

    df0 = dfx[['symbol','datestamp']].groupby('symbol').agg('max').reset_index()
    df0 = df0.rename(columns={"datestamp": "last_investment"})

    df1 = df1.merge(df0, how='left', on='symbol')

    df0 = dfx[['symbol','datestamp']].groupby('symbol').agg('count').reset_index()
    df0 = df0.rename(columns={"datestamp": "investment_count"})

    df2 = df1.merge(df0, how='left', on='symbol')
    df2['total_invested'] = df2['invested']

    return dfx, df2


def stockDescriptionAs_df(sd):
    keys = sd.keys()
    symbol = []
    area = []
    sector = []

    for key in keys:
        symbol.append(key)
        area.append(sd[key]['area'])
        sector.append(sd[key]['sector'])

    dfx = pd.DataFrame.from_dict({
            'symbol':symbol,
            'area':area,
            'sector':sector
                            })

    return dfx
