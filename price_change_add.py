# -*- coding: utf-8 -*-
"""Option_Banknifty.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1cOMZZcpMxYpet10KBuHVIrMHYAUnu2GX
"""

import time
from datetime import datetime,timedelta
import re
from NorenRestApiPy.NorenApi import NorenApi
import pandas as pd
class ShoonyaApiPy(NorenApi):
    def __init__(self):
        NorenApi.__init__(self, host='https://api.shoonya.com/NorenWClientTP/', websocket='wss://api.shoonya.com/NorenWSTP/')        
        global api
        api = self

# import logging
import pyotp
import logging

#enable dbug to see request and responses
#logging.basicConfig(level=logging.DEBUG)
#start of our program
api = ShoonyaApiPy()

#credentials
# Open the file in read mode
#with open('C:\\Users\\Kishan\\Desktop\\Python works\\ShoonyaAPI\\creds.txt', 'r') as f:
#    lines = f.readlines() # Read the file and process the data

# Extract the values from the lines
uid = 'FA56095'          #Your user id like this 'FA12345'
pwd = '2019@Kaveri'        #Your password like this '12345'
vc = 'FA56095_U'           # vendor code 'FA12345_U'
app_key = '218b4b04a2b2b52b04ab277752614825'     #api key 'shjdhjhdasuybashbasjsdhjasbh'
imei = 'abc1234'      #imei anything 'abcd1234'
token = 'F4NPHLFZX334EWQQVGX7IC65D5O27VT2'      #your token ;ABCDEFGHIJKLMNOPQ'
totp = pyotp.TOTP(token).now()

# Use the variables to make API calls or perform other operations
ret = api.login(userid=uid, password=pwd, twoFA=totp , vendor_code=vc, api_secret=app_key, imei=imei)

#print(ret)      #print this to see if login success or not

feed_opened = False
socket_opened = False
feedJson={}

def event_handler_feed_update(tick_data):
    UPDATE = False
    if 'tk' in tick_data:
        token = tick_data['tk']
        timest = datetime.fromtimestamp(int(tick_data['ft'])).isoformat()
        feed_data = {'tt': timest}
        if 'lp' in tick_data:
            feed_data['ltp'] = float(tick_data['lp'])
        if 'ts' in tick_data:
            feed_data['Tsym'] = str(tick_data['ts'])
        if 'oi' in tick_data:
            feed_data['openi'] = float(tick_data['oi'])
        if 'poi' in tick_data:
            feed_data['pdopeni'] = str(tick_data['poi'])
        if 'toi' in tick_data:
            feed_data['toi'] =str(tick_data['toi'])    
        if 'v' in tick_data:
            feed_data['Volume'] = str(tick_data['v']) 
        if 'pc' in tick_data:
            feed_data['per.chg.'] = str(tick_data['pc']) 
        if feed_data:
            UPDATE = True
            if token not in feedJson:
                feedJson[token] = {}
            feedJson[token].update(feed_data)
        if UPDATE:
             pass#print(f'Token:{token} Feed:{feedJson[token]}')

def event_handler_order_update(order_update):
    pass#print(f"order feed {order_update}") 

def open_callback():
    global feed_opened
    feed_opened = True
    print("Websocket opened")

def setupWebSocket():
    global feed_opened
    print("waiting for socket opening")
    api.start_websocket(order_update_callback=event_handler_order_update,
                         subscribe_callback=event_handler_feed_update, 
                         socket_open_callback=open_callback)    
    while(feed_opened==False):        
        pass

setupWebSocket()

sd = api.searchscrip('NFO', 'BANKNIFTY')
sd = (sd['values'])
for Symbol in sd:
     (Symbol['tsym'])
    
tsym_values = [Symbol['tsym'] for Symbol in sd]
dates = [re.search(r'\d+[A-Z]{3}\d+', tsym).group() for tsym in tsym_values]
formatted_dates = [datetime.strptime(date, '%d%b%y').strftime('%Y-%m-%d') for date in dates]
sorted_formatted_dates = sorted(formatted_dates)
sorted_dates = [datetime.strptime(date, '%Y-%m-%d').strftime('%d%b%y').upper() for date in sorted_formatted_dates]
Expiry_date = (sorted_dates[0])
print(Expiry_date)

ret = api.get_quotes(exchange='NSE', token='26009')
ltp = ret.get("lp")
ltp = float(ltp)
ltp_str = str(ltp)
sym = ret.get("symname")
ExpDate = Expiry_date
TYPE = "P"
Strike = int(round(ltp/100,0)*100)

For_token = sym+ExpDate+TYPE+str(Strike)

opc = api.get_option_chain('NFO', For_token , Strike, 1)
opc1 = (opc['values'])

#df = pd.DataFrame(opc["values"])

#print(df)
#print(df['strprc'])
#print(df['strprc'].dtype)
#df['strprc'] = df['strprc'].astype(float)
CE_SYMBOL = sym+ExpDate+'CE'+str(Strike)
PE_SYMBOL = sym+ExpDate+'PE'+str(Strike)
#print(CE_SYMBOL,PE_SYMBOL)
#print(Strike)

def get_token(opc1, tsym):
    for item in opc1:
        if item['tsym'] == tsym:
            return item['token']
    return None

# Test the function
CE_token =  (get_token(opc1, CE_SYMBOL))  # should print '86406'
PE_token = (get_token(opc1, PE_SYMBOL))  # should print '86407'
#print(CE_token ,PE_token)

optionchain = api.get_option_chain('NFO', For_token , Strike, 25)
optionchainsym = (optionchain['values'])
for Symbol in optionchainsym:
     (Symbol['token']) 
    
token= [Symbol['token'] for Symbol in optionchainsym]
modified_tokens = []
for Symbol in optionchainsym:
  token = Symbol['token']
  modified_token = 'NFO|' + token
  modified_tokens.append(modified_token)

print(modified_tokens)



#this will start getting values of option chain
api.subscribe('NSE|26009')
api.subscribe(modified_tokens)

#print this to know values coming in or not
feedJson



import pandas as pd
import time
from openpyxl.utils.cell import coordinate_to_tuple


i = 0
while(i<5000):
    api.subscribe(modified_tokens)
    df = pd.DataFrame.from_dict(feedJson,orient='index', columns=['ltp', 'Tsym','openi','pdopeni','Volume','per.chg.','toi'])
    api.unsubscribe(modified_tokens)
    df.to_csv('data.csv')
    df = pd.read_csv('data.csv')

    import pandas as pd

    # read data from csv
    data = pd.read_csv("data.csv")
    #data = data.sort_values(by='Strike Price', ascending=False)
    # extract spot value and create new column
    spot_value = data.iloc[0]['ltp']
    data['spot'] = spot_value

    # create new columns for instrument name, expiry date, call/put, and strike price
    df['Instrument'] = df['Tsym'].str.extract(r'([A-Z]+)', expand=False)
    df['Expiry'] = df['Tsym'].str.extract(r'([0-9A-Z]+)')[4:]
    df['CP'] = df['Tsym'].str[-6:-5]
    df['Strike'] = df['Tsym'].str[-5:]

    # create separate dataframes for call and put options
    calls = df[df['CP']=='C'].reset_index(drop=True)
    puts = df[df['CP']=='P'].reset_index(drop=True)

    # sort the dataframes by strike price
    calls = calls.sort_values(by=['Strike'])
    puts = puts.sort_values(by=['Strike'])

    # create a new dataframe to store the sorted data
    result = pd.DataFrame()

    df = pd.DataFrame.from_dict(feedJson,orient='index', columns=['ltp', 'Tsym','openi','pdopeni','Volume','per.chg.','toi'])
    api.unsubscribe(modified_tokens)
    df.to_csv('data.csv')
    df = pd.read_csv('data.csv')

    import pandas as pd
    from openpyxl.utils.cell import coordinate_to_tuple
    # read data from csv
    data = pd.read_csv("data.csv")

    # extract spot value and create new column
    spot_value = data.iloc[0]['ltp']
    data['spot'] = spot_value

    # create new columns for instrument name, expiry date, call/put, and strike price
    df['Instrument'] = df['Tsym'].str.extract(r'([A-Z]+)', expand=False)
    df['Expiry'] = df['Tsym'].str.extract(r'([0-9A-Z]+)')[4:]
    df['CP'] = df['Tsym'].str[-6:-5]
    df['Strike'] = df['Tsym'].str[-5:]

    # create separate dataframes for call and put options
    calls = df[df['CP']=='C'].reset_index(drop=True)
    puts = df[df['CP']=='P'].reset_index(drop=True)

    # sort the dataframes by strike price
    calls = calls.sort_values(by=['Strike'])
    puts = puts.sort_values(by=['Strike'])

    # create a new dataframe to store the sorted data
    result = pd.DataFrame()

  # add the columns to the result dataframe in the desired order
    result['Call Volume'] = calls['Volume']
    result['Call PDOpeni'] = calls['pdopeni']
    result['Call Openi'] = calls['openi']
    result['Call ChgOpeni'] = calls['openi'] - calls['pdopeni']
    result['Call per.chg'] = calls['per.chg.']
    result['Call LTP'] = calls['ltp']
    result['Strike Price'] = calls['Strike']
    result['Put LTP'] = puts['ltp']
    result['Put per.chg'] = puts['per.chg.']
    result['Put ChgOpeni'] = puts['openi'] - puts['pdopeni']
    result['Put Openi'] = puts['openi']
    result['Put PDOpeni'] = puts['pdopeni']
    result['Put Volume'] = puts['Volume']
    result['Spot'] = spot_value
    # save the result dataframe to a csv file
    result.to_csv('sorted_data.csv', index=False)
    print('Reciving Data')
    time.sleep(2)
    i = i+1

#print this to see your updated dataframe
df = pd.DataFrame.from_dict(feedJson,orient='index', columns=['ltp', 'Tsym','openi','pdopeni','Volume'])
df





