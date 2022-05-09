import asyncio
from datetime import datetime
import aiohttp
import os
import platform
import time
# To work with the .env file

import requests
import pandas as pd
import talib.abstract as ta
from pyti.simple_moving_average import simple_moving_average as ma


def GetTradableSymbols():
    base = 'https://api3.binance.com'
    endpoint = '/api/v3/exchangeInfo'

    url = base + endpoint

    # download data
    #data = requests.get(url)
    while True:
        try:
            data = requests.get(url)
            break
        except (ConnectionError, TimeoutError):
            print("Will retry again in a little bit")
            print("Please Wait ....")
        except Exception as e:
            print(e)
            print("Please Wait ....")
        time.sleep(5)

    data2 = data.json()
    symbol_list = []
    for pair in data2['symbols']:
        if pair['status'] == 'TRADING':
            if pair['quoteAsset'] == 'USDT':
                if ("up" not in pair['symbol'].lower()) and ("down" not in pair['symbol'].lower()) and \
                        ("busd" not in pair['symbol'].lower()) and ("usdc" not in pair['symbol'].lower()) and ("tusd" not in pair['symbol'].lower()) and \
                        ("pax" not in pair['symbol'].lower()):
                    symbol_list.append(pair['symbol'])
    return symbol_list


url = 'https://api3.binance.com/api/v3/klines?&symbol={}&interval= {}&limit=200'

# url = 'https://www.alphavantage.co/query?function=OVERVIEW&symbol={}&apikey={}'
# symbols = ['BTCUSDT','ETHUSDT','LTCUSDT','BNBUSDT','BCHUSDT','ADAUSDT','ZECUSDT','THETAUSDT','TRBUSDT','SUSHIUSDT','EOSUSDT','DOGEUSDT']

symbols = GetTradableSymbols()
results = []
tf = '1h'
print(symbols)
start = time.time()


def get_tasks(session):
    tasks = []
    for symbol in symbols:
        url = 'https://api3.binance.com/api/v3/klines?&symbol=' + \
            symbol+'&interval='+tf+'&limit=200'
        tasks.append(asyncio.create_task(session.get(url)))
        # t = {'symbol': symbol, 'tsk': asyncio.create_task(session.get(url))}
        # tasks.append(t)
    return tasks


async def get_symbols():
    async with aiohttp.ClientSession() as session:
        tasks = get_tasks(session)
        # you could also do
        # tasks = [session.get(URL.format(symbol, API_KEY), ssl=False) for symbol in symbols]
        responses = await asyncio.gather(*tasks)
        for response in responses:
            results.append(await response.json())

if platform.system() == 'Windows':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
asyncio.run(get_symbols())


end = time.time()
total_time = end - start
print("It took {} seconds to make {} API calls".format(total_time, len(symbols)))
print('You did it!')

i = 0
for res in results:
    df = pd.DataFrame.from_dict(res)
    df = df.drop(range(6, 12), axis=1)
    # rename columns
    col_names = ['time', 'open', 'high', 'low', 'close', 'volume']
    df.columns = col_names

    # transform values from strings to floats
    for col in col_names:
        df[col] = df[col].astype(float)




    # if len(df) >= 180:
    #     df['ema85'] = ta.EMA(df['close'], 85)
    if len(df) >= 180:
        
        df['date'] = pd.to_datetime(df['time'] * 1000000, infer_datetime_format=True)
        # add the moving averages
        df['ma9'] = ma(df['close'].tolist(), 9)
        df['ma18'] = ma(df['close'].tolist(), 18)
        df['ma27'] = ma(df['close'].tolist(), 27)
        df['ma36'] = ma(df['close'].tolist(), 36)
        df['ma45'] = ma(df['close'].tolist(), 45)
        df['ema85'] = ta.EMA(df['close'], 85)
        df['ema'] = ta.EMA(df['close'], 45)
        df['cci'] = ta.CCI(df['close'], df['high'], df['low'], 20)
        df['rsi'] = ta.RSI(df['close'], 14)
        df['mfi'] = ta.MFI(df['high'], df['low'], df['close'], df['volume'])
        df['macd'], df['macdsignal'], df['macdhist'] = ta.MACD(df['close'], 12, 26, 9)

        # Ichimoku Calculation
        nine_period_high = df['high'].rolling(window=9).max()
        nine_period_low = df['low'].rolling(window=9).min()
        # Conversion Line
        df['tenkansen'] = (nine_period_high + nine_period_low) / 2
        period26_high = df['high'].rolling(window=26).max()
        period26_low = df['low'].rolling(window=26).min()
        # Base Line
        df['kijunsen'] = (period26_high + period26_low) / 2
        # Leading Span A
        df['senkou_a'] = ((df['tenkansen'] + df['kijunsen']) / 2).shift(26)
        df['senkou_a_f'] = (df['tenkansen'] + df['kijunsen']) / 2
        period52_high = df['high'].rolling(window=52).max()
        period52_low = df['low'].rolling(window=52).min()
        # Leading Span B
        df['senkou_b'] = ((period52_high + period52_low) / 2).shift(26)
        df['senkou_b_f'] = (period52_high + period52_low) / 2
        # Lagging Span
        df['chikouspan'] = df['close'].shift(-26)
        df['ema85'] = ta.EMA(df['close'], 85)
        df.to_csv(f'csv\{symbols[i]}-{datetime.now().strftime("%Y-%m-%d_%H-%M")}-{tf}.csv')
    # break
        # current_ema85 = round(df['ema85'][len(df['close']) - 1], 6)
    # current_ema85 = round(df['close'][len(df['close']) - 1], 6)
        # print(f'{symbols[i]} ema85:{tf}: {current_ema85}')
    # df.to_pickle(f"{symbols[i]}.pkl")
    

    i += 1

end2 = time.time()
total_time2 = end2 - start
print("It took {} seconds to make {} API calls".format(total_time2, len(symbols)))
print('You did it!')
