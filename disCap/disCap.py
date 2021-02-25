import yfinance as yf
import matplotlib.pyplot as plt
import matplotlib
from datetime import datetime
import numpy as np
import pandas as pd
import urllib
import json 

def retrieve_current_cryptocoin_price(coin):
    ''' for cryptocurrency coin, return current price in US Dollars '''
    current_price = None
    if coin == 'eth':
        coin_json = urllib.request.urlopen("https://data.messari.io/api/v1/assets/eth/metrics").read().decode("utf-8")
    elif coin == 'btc':
        coin_json = urllib.request.urlopen("https://data.messari.io/api/v1/assets/btc/metrics").read().decode("utf-8")
    else:
        coin_json = None
    coin_json = json.loads(coin_json)
    current_price = coin_json['data']['market_data']['price_usd']
    return current_price


def get_stock_data(symbol,duration):
    '''
    for stock with sticker symbol, retrieve closing data for days in duration, return as a dataframe

    Parameters:
        symbol (string): stock symbol
        duration (string): specifies days to look backwards.  Example: '180d', specifies 180 days.
    Returns:
        df (dataframe): dataframe of form ['Date','Symbol','Close','Volume']

    '''
    def mkdays(val):
        return val.days
    def mkdaystr(val):
        return val.strftime('%Y.%m.%d')
    df = yf.Ticker(symbol).history(duration)
    df['Company'] = symbol
    df['Date'] = df.index
    df.reset_index(drop=True, inplace=True)
    vals = df.Date - df.Date[0]
    df['Days'] = list( map( mkdays, vals ) )
    df['Daystring'] = list( map( mkdaystr, df.Date ) )
    # df = df[['Date','Company','Close','Volume']]
    return df
    
    
def get_stock_recent_statistics(symbol,duration):
    df = get_stock_data(symbol,duration)
    median = np.median( df.close ) 
    avg = np.median( df.close ) 
    stdv = np.std( df.close ) 

def add_investments(df,investments,symbol):
    '''
    df is a dataframe of yahoo-finance data of form ['Date','Symbol','Close','Volume'] for some duration.
    symbol is the stock symbol of interest
    this function pairs investments made with dates in the the dataframe and returns new dataframe with additional
    field ['Date','Symbol','Close','Volume','value','shares','gain','spent']
    '''
    df['shares'] = 0.00
    df['spent'] = 0.00
    df['gain'] = 0.00
    for invest in investments[symbol]:
        df = create_invested(invest,df)
        df['value'] = df['Close'] * df['shares']
        df.loc[( (df['shares']>0.00) ),'gain'] = \
           df.loc[( (df['shares']>0.00) ),'value']/df.loc[( (df['shares']>0.00) ),'spent']
    return df

def create_invested(invested,df):
    ''' Called from add_investments, adds specific investment instances starting at appropriate data'''
    df.loc[( (df.Daystring>=invested[0]) ),'shares'] = \
        df.loc[( (df.Daystring>=invested[0]) ),'shares'] + invested[2]
    df.loc[( (df.Daystring>=invested[0]) ),'spent'] = \
        df.loc[( (df.Daystring>=invested[0]) ),'spent'] + invested[1]
    return df


def doubleplot_(df, showeach, title_string, window):
    '''
    for a df created by add_investments, create two figures:
    Top:  Value Owned [blue dots] and invested [green dots] as function of dates
    Bottom:  Close stock price as function of dates
    '''
    x = df.Days

    fig, ax1 = plt.subplots()
    fig.set_figheight(3)
    fig.set_figwidth(9)

    ax1.set_xlabel('Date')
    ax1.set_ylabel('Value Owned[$]', color='black')
    ax1.plot(x, df.value, linestyle='None', marker='.', color='blue', markersize=5)
    ax1.plot(x, df.spent, linestyle='None', marker='.', color='green', markersize=10)

    #fig.tight_layout()  # otherwise the right y-label is slightly clipped

    vals, labs = thinticks(df, showeach)
    trap = plt.xticks(vals, labs)
    matplotlib.pyplot.sca(ax1)
    plt.xticks(rotation=90)
    plt.title(title_string)

    plt.show()
    standard_plot(df, showeach, '', window)

def thinticks(df, showeach):
    val = df.Days
    lab = df.Date
    vals = []
    labs = []
    k = 0
    while k < len(val):
        vals.append( val[k] )
        labs.append( lab[k].strftime('%Y.%m.%d') )
        k = k + showeach
    return vals, labs

def standard_plot(df, showeach, title_string, window):
    def findwindowave(values, window):
        mx = len(values)
        windowave = []
        for k in range(0,mx):
            left = right = k
            if k > window:
                left = k - window
            if (k+window) < mx:
                right = k + window
            windowave.append( np.average( values[left:right] ) )
        return windowave

    plt.figure(figsize=(9,3))

    x, y = df.Days, df.Close
    plt.scatter(x, y,  s=1, c='black')
    plt.scatter(x, findwindowave(y, window),  s=10, c='black')
    #plt.scatter(x, df.Low,  s=1, c='blue')
    vals, labs = thinticks(df, showeach)
    trap = plt.xticks(vals, labs, rotation=90)
    plt.ylabel('Close $')
    plt.xlabel('Date')
    plt.title(title_string)

    plt.show()

def findwindowave(values, window):
    mx = len(values)
    windowave = []
    for k in range(0,mx):
        left = right = k
        if k > window:
            left = k - window
        if (k+window) < mx:
            right = k + window
        windowave.append( np.average( values[left:right] ) )
    return windowave

def rgb_gain(gain, mingain, green_point, maxgain):
    ''' Returns a list of rgb tupples, that go from red to yellow then green to blue
    For the list gain, return a list of tupples that are scored by along gain
    mingain is the gain value which will be perfectly RED
       colors will linearlly approach YELLOW as they approach green_point
    green_point is the gain value which is green and colors approach pure blue at maxgain
    '''
    clrs = []
    for gp in gain:
        if gp < green_point:
            # (1,0,0) -> (5/11,5/11,1/11)
            # slider = 0 when gp==greenpoint, 1 when gp = mingain
            slider = (green_point - gp) / (green_point - mingain)
            rc = 1.00
            gc = (1-slider)
            bc = 0
            clrs.append((rc,gc,bc))
        if gp >= green_point:
            # gp == green_point, slider = 0
            slider = (gp - green_point) / (maxgain - green_point)
            bc = slider
            gc = 1.00 - bc
            clrs.append((0,gc,bc))
    return clrs

def investmentsAs_df(investments, specialvalues):
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
    close = []

    for key in keys:
        if key not in specialvalues.keys():
            df = yf.Ticker(key).history('1d')
        invest_list = investments[key]
        for v in investments[key]:
            keydates.append('{}:{}'.format(key,v[0]))
            datestamp.append(v[0])
            invested.append(v[1])
            shares.append(v[2])
            symbol.append(key)
            if key not in specialvalues.keys():
                try:
                    close.append( df.Close[0] )
                except:
                    close.append( v[1] )
            else:
                close.append( specialvalues[key] )

    dfx = pd.DataFrame.from_dict({
            'keydates':keydates,
            'symbol':symbol,
            'datestamp':datestamp,
            'invested':invested,
            'shares':shares,
            'close':close
                            })
    return dfx


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


def mklab(s1,s2,s3,s4,s5):
    return '{0}\ninvested:{1:6.2f}\nvalue:{2:6.2f}\ngain:{3:6.3f}\nshares:{4:6.3f}'.format(s1,s2,int(s3),s4,s5)


def todayValueAs_df(investments_df):
    df0 = investments_df[['symbol','invested','shares']].groupby('symbol').agg('sum').reset_index()
    df1 = investments_df[['symbol','close','datestamp']].groupby('symbol').agg('min').reset_index()

    df2 = df1.merge(df0, how='left', on='symbol')
    df1 = df2.rename(columns={"datestamp": "first_investment"})

    df0 = investments_df[['symbol','datestamp']].groupby('symbol').agg('max').reset_index()
    df0 = df0.rename(columns={"datestamp": "last_investment"})

    df1 = df1.merge(df0, how='left', on='symbol')

    df0 = investments_df[['symbol','datestamp']].groupby('symbol').agg('count').reset_index()
    df0 = df0.rename(columns={"datestamp": "investment_count"})

    df2 = df1.merge(df0, how='left', on='symbol')

    df2['value'] = df2['shares'] * df2['close']
    df2['gain'] = df2['value']/df2['invested']

    total_invested = sum( df2['invested'] )
    total_value = sum( df2['value'] )

    df2['percentage_value'] = df2['value']/total_value
    df2['percentage_invested'] = df2['invested']/total_value
    df2['effective_share_price'] = df2['invested']/df2['shares']

    fields = ['symbol','investment_count','first_investment',
                       'last_investment','close','effective_share_price','shares',
                       'invested','value', 'gain',
                       'percentage_value', 'percentage_invested']

    return df2[fields], total_invested, total_value
