import json 
from urllib.request import urlopen
import pandas as pd

'''
https://financialmodelingprep.com
has an API which has some better features than Yahoo Finance.
API also allows access to the Cryptocurrency data and quarterly metrics.
These functions are a revision of disCap library to use this more convenient API.
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
    
      Copied from https://financialmodelingprep.com
    """
    response = urlopen(url)
    data = response.read().decode("utf-8")
    return json.loads(data)
    

def get_current_metrics(symbol, api_key):
    '''
    param: symbol - ticker symbol for a stock
    param: api_key - API key required for access
    returns: result - json of data for stock of symbol
    '''
    prefix = 'https://financialmodelingprep.com/api/v3/profile/'
    url = '{}{}?apikey={}'.format(prefix,symbol, api_key)
    result = get_jsonparsed_data(url)
    return result


def get_historic_data(symbol, api_key):
    '''
    param: symbol - ticker symbol for a stock
    param: api_key - API key required for access
    returns: df - dataframe. historical daily close data for stock symbol
    '''
    def extract_history(result):
        '''
        param: result, get_jsonparsed_data returns result which is json.
        returns: df - dataframe created from reshaping json result into a more useful pandas df
        '''
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
    df = extract_history(result)
    return df
 
 
 def get_quarterly_metrics(symbol, api_key):
    '''
    param: symbol - ticker symbol for a stock
    param: api_key - API key required for access
    returns: df - dataframe. historical quarterly financial data for stock symbol
    '''
    def extract_history(result):
        '''
        param: result, get_jsonparsed_data returns result which is json.
        returns: df - dataframe created from reshaping json result into a more useful pandas df
        '''
        start_date =[]
        revenue = []
        grossProfit = []
        for token in result:
            start_date.append(token['date'])
            revenue.append(token['revenue'])
            grossProfit.append(token['grossProfit'])
        df = pd.DataFrame.from_dict({ 'symbol':symbol, 'start_date':start_date, 'revenue':revenue,
                                      'grossProfit':grossProfit})
        end_date = list( df['start_date'] )
        end_date = end_date[:-1]
        end_date.insert(0,None)
        df['end_date'] = end_date
        fields = ['symbol','start_date','end_date','revenue','grossProfit']
        return df[fields]

    prefix = 'https://financialmodelingprep.com/api/v3/income-statement/'
    url = '{}{}?period=quarter&limit=400&apikey={}'.format(prefix,symbol, api_key)
    result = get_jsonparsed_data(url)
    return extract_history(result)