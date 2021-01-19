import yfinance as yf
import pandas as pd

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