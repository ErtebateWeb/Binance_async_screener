import asyncio
import aiohttp
import os
import platform
import time
# To work with the .env file

import requests
import pandas as pd
import talib.abstract as ta


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
                        ("busd" not in pair['symbol'].lower()) and ("tusd" not in pair['symbol'].lower()) and \
                        ("pax" not in pair['symbol'].lower()):
                    symbol_list.append(pair['symbol'])
    return symbol_list


url = 'https://api3.binance.com/api/v3/klines?&symbol={}&interval= {}&limit=200'

# url = 'https://www.alphavantage.co/query?function=OVERVIEW&symbol={}&apikey={}'
# symbols = ['BTCUSDT','ETHUSDT','LTCUSDT','BNBUSDT','BCHUSDT','ADAUSDT','ZECUSDT','THETAUSDT','TRBUSDT','SUSHIUSDT','EOSUSDT','DOGEUSDT']

symbols = GetTradableSymbols()
results = []
tf = '4h'
print(symbols)
start = time.time()


def get_tasks(session):
    tasks = []
    for symbol in symbols:
        url = 'https://api3.binance.com/api/v3/klines?&symbol=' + \
            symbol+'&interval=1h&limit=200'
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
    if len(df) >= 180:
        df['ema85'] = ta.EMA(df['close'], 85)

    # break
        current_ema85 = round(df['ema85'][len(df['close']) - 1], 6)
    # current_ema85 = round(df['close'][len(df['close']) - 1], 6)
        print(f'{symbols[i]} ema85: {current_ema85}')
    i += 1

end = time.time()
total_time = end - start
print("It took {} seconds to make {} API calls".format(total_time, len(symbols)))
print('You did it!')
