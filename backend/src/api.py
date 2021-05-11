import asyncio
import requests
from fastapi import FastAPI, WebSocket, Depends, Security
from fastapi_auth0 import Auth0, Auth0User
from fastapi.middleware.cors import CORSMiddleware
from websockets.exceptions import ConnectionClosedError
from pydantic import BaseModel
from typing import List
from functools import cached_property
from analyzer import message_analyzer
from binance.exceptions import *
from binance.enums import *
import binance.client
import kucoin
import discord
import telethon
import math
import decimal
import json
import time


origins = [
    "http://localhost:8000",
]

api = FastAPI(title="botqoin",
              description="One bot to rule them all.",
              version="0.2.0",
              docs_url='/api/docs',
              redoc_url='/api/redoc',
              openapi_url='/api/openapi.json',
              swagger_ui_oauth2_redirect_url='/api/docs/oauth2-redirect')

api.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Channels(BaseModel):
    discord_channels: dict
    telegram_channels: dict


class Credentials(BaseModel):
    binance_api_key: str
    binance_api_secret: str
    kucoin_api_key: str
    kucoin_api_secret: str
    kucoin_api_passphrase: str


class TradeInfo(BaseModel):
    symbol: str


class BotInfo(BaseModel):
    profit_percentage_1: str
    profit_percentage_2: str
    profit_percentage_3: str
    sell_method: str
    funds_quantity: str
    trade_pair: str
    trade_platform: str


class DiscordManager:
    dc_ch_list = []

    def __init__(self):
        super().__init__()
        self.client.event(self.on_message)
        self.token = "NTYyOTc0OTMzMDg1MzIzMjY0.YEPkaQ.qtaksxyYJQhNvWSLx2APvOZraCM"

    @cached_property
    def client(self):
        return discord.Client()

    @staticmethod
    async def on_message(message):
        global current_message, current_symbol
        if message.channel.category_id in discord_channel_dictionary:
            if not message.content == "":
                symbol = message_analyzer(message.content, binance_trade_flag, kucoin_trade_flag, symbol_dictionary,
                                          trade_pair)
                if symbol != "":
                    print(symbol)
                    current_message = message.content
                    current_symbol = symbol
                    await initialize_trade(symbol)
                    return
            try:
                embed_description = message.embeds[0].description
                symbol = message_analyzer(embed_description, binance_trade_flag, kucoin_trade_flag, symbol_dictionary,
                                          trade_pair)
                if symbol != "":
                    current_message = embed_description
                    current_symbol = symbol
                    await initialize_trade(symbol)
                    return
            except:
                pass
            try:
                embed_value = message.embeds[0].fields[0].value
                symbol = message_analyzer(embed_value, binance_trade_flag, kucoin_trade_flag, symbol_dictionary,
                                          trade_pair)
                if symbol != "":
                    current_message = embed_value
                    current_symbol = symbol
                    await initialize_trade(symbol)
                    return
            except:
                current_message = message.content
                current_symbol = "No symbol found"
                return

    async def start(self):
        await self.client.start(self.token, bot=False)


class TelegramManager:
    tg_ch_list = []

    def __init__(self):
        super().__init__()
        self.client.add_event_handler(self.on_message, telethon.events.NewMessage)

    @cached_property
    def client(self):
        return telethon.TelegramClient('botQoin', 3112726, "15d793b32dc85708032b761fbaec12f6")

    @staticmethod
    async def on_message(event):
        global current_message, current_symbol
        if event.chat.username in telegram_channel_dictionary:
            symbol = message_analyzer(event.message.message, binance_trade_flag, kucoin_trade_flag, symbol_dictionary,
                                      trade_pair)
            if symbol != "" or None:
                current_message = event.message.message
                current_symbol = symbol
                await initialize_trade(symbol)
            else:
                current_message = event.message.message
                current_symbol = "No symbol found."

    async def start(self):
        await self.client.start()


class WebsocketConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    @staticmethod
    async def send_personal_message(message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


websocket_manager = WebsocketConnectionManager()


# botqoin variables
telegram_channel_dictionary = {}
discord_channel_dictionary = {}

binance_client = binance.client.Client()
kucoin_client = kucoin.Client()

binance_trade_flag = False
kucoin_trade_flag = False

symbol_dictionary = {}

profit_percentage_1 = 0
profit_percentage_2 = 0
profit_percentage_3 = 0
funds_quantity = 0
sell_method = None
trade_pair = None

current_message = ""
current_symbol = ""
current_status = ""

auth = Auth0(domain='botqoin.us.auth0.com',
             api_audience='botqoin',
             scopes={"read:all": "read-all"})


async def precision(number: float, decimals):
    try:
        decimals = int(decimals)
    except:
        raise TypeError("Decimal places: failed to cast as an integer.")
    if decimals < 0:
        raise ValueError("Decimal places has to be 0 or more.")
    elif decimals == 0:
        return math.floor(number)

    factor = 10 ** decimals
    mf = math.floor(number * factor) / factor
    return f'{mf:.{decimals}f}'


async def get_auth0_access_token():
    url = "https://botqoin.us.auth0.com/oauth/token"
    data = json.dumps({"client_id": "c3gy7WhgX6HIjdHzTWdRn6vQ8BIz2iIg",
                       "client_secret": "HodmVihOGeuOq_8jsgcAWzaT4H4v0SYF5FIuimv-gJsTBuzUcmc2JvQWUnwzNMOj",
                       "audience": "https://botqoin.us.auth0.com/api/v2/",
                       "grant_type": "client_credentials"})
    headers = {"content-type": "application/json"}
    response = requests.request("POST", url, data=data, headers=headers)
    return response.json()['access_token']


async def trader_start(credentials):
    global binance_client, kucoin_client, discord_channel_dictionary, telegram_channel_dictionary

    with open("/home/ubuntu/botqoin/backend/resources/channels.json") as channels:
        channel_list = json.load(channels)
        discord_channel_dictionary = channel_list["discord_channels"]
        telegram_channel_dictionary = channel_list["telegram_channels"]
        discord_channel_dictionary = {int(k): str(v) for k, v in discord_channel_dictionary.items()}

    if binance_trade_flag:
        binance_client = binance.client.Client(credentials['binance_api_key'],
                                               credentials['binance_api_secret'])

    elif kucoin_trade_flag:
        kucoin_client = kucoin.Client(credentials['kucoin_api_key'],
                                      credentials['kucoin_api_secret'],
                                      credentials['kucoin_api_passphrase'])

    await fetch_symbol_dict()


async def trader_stop():
    global binance_client, kucoin_client

    binance_client = None
    kucoin_client = None


async def fetch_symbol_dict():
    global symbol_dictionary

    symbol_dictionary.clear()

    if binance_trade_flag:
        exchange_info = binance_client.get_exchange_info()
        for symbol in exchange_info['symbols']:
            for filt in symbol['filters']:
                if 'PRICE_FILTER' in filt['filterType']:
                    symbol_dictionary[symbol['symbol']] = [str(float(filt['tickSize']))[-1],
                                                           str(symbol['baseAssetPrecision'])]

    elif kucoin_client:
        exchange_info = kucoin_client.get_symbols()
        for symbol in exchange_info:
            price_digit = decimal.Decimal(symbol['priceIncrement'])
            price_precision_minus = price_digit.as_tuple().exponent
            price_precision = str(price_precision_minus).replace("-", "")
            base_digit = decimal.Decimal(symbol['baseIncrement'])
            base_precision_minus = base_digit.as_tuple().exponent
            base_precision = str(base_precision_minus).replace("-", "")
            symbol_dictionary[symbol['symbol']] = [price_precision, base_precision]


async def initialize_trade(symbol):

    async def calculate_sell_prices(bp):
        sp1 = await precision(((bp * (int(profit_percentage_1) / 100)) + bp),
                              symbol_dictionary[symbol][0])
        sp2 = None
        sp3 = None
        if sell_method == "5050":
            sp2 = await precision(((bp * (int(profit_percentage_2) / 100)) + bp),
                                  symbol_dictionary[symbol][0])
        elif sell_method == "502525":
            sp2 = await precision(((bp * (int(profit_percentage_2) / 100)) + bp),
                                  symbol_dictionary[symbol][0])
            sp3 = await precision(((bp * (int(profit_percentage_3) / 100)) + bp),
                                  symbol_dictionary[symbol][0])
        return sp1, sp2, sp3

    async def calculate_sell_sizes(bs):
        ss1 = None
        ss2 = None
        if sell_method == "5050":
            mod2 = bs % 2
            pss = (bs - mod2) / 2
            ss1 = await precision((pss + mod2), symbol_dictionary[symbol][1])
            ss2 = await precision(pss, symbol_dictionary[symbol][1])
        elif sell_method == "502525":
            mod4 = bs % 4
            pss = (bs - mod4) / 4
            ss1 = await precision(((pss * 2) + mod4), symbol_dictionary[symbol][1])
            ss2 = await precision(pss, symbol_dictionary[symbol][1])
        return ss1, ss2

    start_timestamp = time.time() * 1000

    global binance_trade_flag, kucoin_trade_flag, current_status

    if binance_trade_flag:
        binance_trade_flag = False
        try:
            buy_order = binance_client.create_order(
                symbol=symbol,
                side=SIDE_BUY,
                type=ORDER_TYPE_MARKET,
                quoteOrderQty=funds_quantity)
            print(buy_order)
        except BinanceRequestException as exception:
            print(exception)
            current_status = str(exception) + " @ Buy Order"
            return
        except BinanceAPIException as exception:
            print(exception)
            current_status = str(exception) + " @ Buy Order"
            return

        buy_end_timestamp = time.time() * 1000

        total_buy_price = 0
        total_buy_quantity = 0

        for part in buy_order['fills']:
            part_buy_quantity = int(float(part['qty']))
            part_buy_price = float(part['price']) * part_buy_quantity
            total_buy_quantity += part_buy_quantity
            total_buy_price += part_buy_price

        buy_price = total_buy_price / total_buy_quantity
        buy_price_precise = await precision((total_buy_price / total_buy_quantity), symbol_dictionary[symbol][0])

        sell_price_1, sell_price_2, sell_price_3 = await calculate_sell_prices(buy_price)

        if sell_method == "100":
            sell_size_100 = await precision(total_buy_quantity, symbol_dictionary[symbol][1])
            try:
                sell_order = binance_client.order_limit_sell(
                    symbol=symbol,
                    quantity=sell_size_100,
                    price=sell_price_1)
            except BinanceRequestException as exception:
                print(exception)
                current_status = str(exception) + " @ Sell Order"
                return
            except BinanceAPIException as exception:
                print(exception)
                current_status = str(exception) + " @ Sell Order"
                return

            sell_end_timestamp = time.time() * 1000

            buy_time = str(int(buy_end_timestamp - start_timestamp))
            sell_time = str(int(sell_end_timestamp - buy_end_timestamp))

            current_status = "Market buy @ {} in {}ms   " \
                             "Limit sell @ {} in {}ms".format(buy_price_precise,
                                                              buy_time,
                                                              sell_price_1,
                                                              sell_time)

            print(sell_order)

            await asyncio.sleep(2)

            try:
                order = binance_client.get_order(
                    symbol=symbol,
                    orderId=sell_order['orderId'])
            except BinanceRequestException as exception:
                print(exception)
                current_status = str(exception) + " @ Sell Order Check"
                return
            except BinanceAPIException as exception:
                print(exception)
                current_status = str(exception) + " @ Sell Order Check"
                return

            sell_order_check = order
            print(sell_order_check)

            if sell_order_check['status'] == "NEW":
                try:
                    order = binance_client.cancel_order(
                        symbol=symbol,
                        orderId=sell_order_check['orderId'])
                except BinanceRequestException as exception:
                    print(exception)
                    current_status = str(exception) + " @ Sell Order Cancel"
                    return
                except BinanceAPIException as exception:
                    print(exception)
                    current_status = str(exception) + " @ Sell Order Cancel"
                    return

                sell_order_cancel = order
                print(sell_order_cancel)

                print(buy_order['origQty'])

                try:
                    order = binance_client.create_order(
                        symbol=symbol,
                        side=SIDE_SELL,
                        type=ORDER_TYPE_MARKET,
                        quantity=precision(total_buy_quantity, symbol_dictionary[symbol][1]))
                    sell_order_market = order
                    print(sell_order_market)
                except BinanceRequestException as exception:
                    print(exception)
                    print("@ Sell Order Market")
                    current_status = str(exception) + " @ Sell Order Market"
                    return
                except BinanceAPIException as exception:
                    print(exception)
                    print("@ Sell Order Market")
                    current_status = str(exception) + " @ Sell Order Market"
                    return
                print(sell_order_market)

        elif sell_method == "5050":
            sell_5050_size_1, sell_5050_size_2 = await calculate_sell_sizes(total_buy_quantity)
            try:
                sell_order_1 = binance_client.order_limit_sell(
                    symbol=symbol,
                    quantity=sell_5050_size_1,
                    price=sell_price_1)
                sell_order_2 = binance_client.order_limit_sell(
                    symbol=symbol,
                    quantity=sell_5050_size_2,
                    price=sell_price_2)
            except BinanceRequestException as exception:
                print(exception)
                current_status = str(exception) + " @ Sell Order"
                return
            except BinanceAPIException as exception:
                print(exception)
                current_status = str(exception) + " @ Sell Order"
                return

            sell_end_timestamp = time.time() * 1000

            buy_time = str(int(buy_end_timestamp - start_timestamp))
            sell_time = str(int(sell_end_timestamp - buy_end_timestamp))

            current_status = "Market buy @ {} in {}ms   " \
                             "Limit sells @ {} and {} in {}ms".format(buy_price_precise,
                                                                      buy_time,
                                                                      sell_price_1,
                                                                      sell_price_2,
                                                                      sell_time)
            print(sell_order_1)
            print(sell_order_2)

        elif sell_method == "502525":
            sell_502525_size_1, sell_502525_size_2 = await calculate_sell_sizes(total_buy_quantity)
            try:
                sell_order_1 = binance_client.order_limit_sell(
                    symbol=symbol,
                    quantity=sell_502525_size_1,
                    price=sell_price_1)
                sell_order_2 = binance_client.order_limit_sell(
                    symbol=symbol,
                    quantity=sell_502525_size_2,
                    price=sell_price_2)
                sell_order_3 = binance_client.order_limit_sell(
                    symbol=symbol,
                    quantity=sell_502525_size_2,
                    price=sell_price_3)

            except BinanceRequestException as exception:
                print(exception)
                current_status = str(exception) + " @ Sell Order"
                return
            except BinanceAPIException as exception:
                print(exception)
                current_status = str(exception) + " @ Sell Order"
                return

            sell_end_timestamp = time.time() * 1000

            buy_time = str(int(buy_end_timestamp - start_timestamp))
            sell_time = str(int(sell_end_timestamp - buy_end_timestamp))

            current_status = "Market buy @ {} in {}ms   " \
                             "Limit sells @ {}, {} and {} in {}ms".format(buy_price_precise,
                                                                          buy_time,
                                                                          sell_price_1,
                                                                          sell_price_2,
                                                                          sell_price_3,
                                                                          sell_time)

            print(sell_order_1)
            print(sell_order_2)
            print(sell_order_3)

        return "Binance Trade Done"

    if kucoin_trade_flag:
        kucoin_trade_flag = False

        try:
            buy_order = kucoin_client.create_order(order_side="buy",
                                                   order_type="market",
                                                   order_symbol=symbol,
                                                   order_funds=funds_quantity,)
        except kucoin.APIException as exception:
            print(exception)
            current_status = str(exception) + " @ Market Buy Order"
            return

        buy_end_timestamp = time.time() * 1000

        buy_order_id = buy_order['orderId']
        buy_order = kucoin_client.get_order(order_id=buy_order_id)

        buy_size = float(buy_order['dealSize'])
        while buy_size == 0:
            buy_order = kucoin_client.get_order(order_id=buy_order_id)
            buy_size = float(buy_order['dealSize'])

        buy_price = (float(buy_order['dealFunds']) / float(buy_size))
        buy_price_precise = await precision((float(buy_order['dealFunds']) / float(buy_size)),
                                            symbol_dictionary[symbol][0])

        sell_price_1, sell_price_2, sell_price_3 = await calculate_sell_prices(buy_price)

        if sell_method == "100":
            sell_100_size = await precision(buy_size, symbol_dictionary[symbol][1])
            try:
                sell_order = kucoin_client.create_order(order_side="sell",
                                                        order_type="limit",
                                                        order_symbol=symbol,
                                                        order_size=sell_100_size,
                                                        order_price=sell_price_1)
            except kucoin.APIException as exception:
                print(exception)
                current_status = str(exception) + " @ Limit Sell Order"
                return

            sell_end_timestamp = time.time() * 1000

            buy_time = str(int(buy_end_timestamp - start_timestamp))
            sell_time = str(int(sell_end_timestamp - buy_end_timestamp))

            current_status = "Market buy @ {} in {}ms \n"\
                             "Limit sell @ {} in {}ms".format(buy_price_precise,
                                                              buy_time,
                                                              sell_price_1,
                                                              sell_time)
            sell_order_id = sell_order['orderId']
            sell_order = kucoin_client.get_order(order_id=sell_order_id)

            print(buy_order)
            print("Executed in {}ms".format(buy_time))
            print(sell_order)
            print("Executed in {}ms".format(sell_time))

        elif sell_method == "5050":
            sell_5050_size_1, sell_5050_size_2 = await calculate_sell_sizes(buy_size)
            try:
                sell_order_1 = kucoin_client.create_order(order_side="sell",
                                                          order_type="limit",
                                                          order_symbol=symbol,
                                                          order_size=sell_5050_size_1,
                                                          order_price=sell_price_1)
                sell_order_2 = kucoin_client.create_order(order_side="sell",
                                                          order_type="limit",
                                                          order_symbol=symbol,
                                                          order_size=sell_5050_size_2,
                                                          order_price=sell_price_2)
            except kucoin.APIException as exception:
                print(exception)
                current_status = str(exception) + " @ Limit Sell Orders"
                return

            sell_end_timestamp = time.time() * 1000

            buy_time = str(int(buy_end_timestamp - start_timestamp))
            sell_time = str(int(sell_end_timestamp - buy_end_timestamp))

            current_status = "Market buy @ {} in {}ms   " \
                             "Limit sells @ {} and {} in {}ms".format(buy_price_precise,
                                                                      buy_time,
                                                                      sell_price_1,
                                                                      sell_price_2,
                                                                      sell_time)
            sell_order_1_id = sell_order_1['orderId']
            sell_order_2_id = sell_order_2['orderId']
            sell_order_1 = kucoin_client.get_order(order_id=sell_order_1_id)
            sell_order_2 = kucoin_client.get_order(order_id=sell_order_2_id)

            print(buy_order)
            print("Executed in {}ms".format(buy_time))
            print(sell_order_1)
            print(sell_order_2)
            print("Executed in {}ms".format(sell_time))

        elif sell_method == "502525":
            sell_502525_size_1, sell_502525_size_2 = await calculate_sell_sizes(buy_size)
            try:
                sell_order_1 = kucoin_client.create_order(order_side="sell",
                                                          order_type="limit",
                                                          order_symbol=symbol,
                                                          order_size=sell_502525_size_1,
                                                          order_price=sell_price_1)
                sell_order_2 = kucoin_client.create_order(order_side="sell",
                                                          order_type="limit",
                                                          order_symbol=symbol,
                                                          order_size=sell_502525_size_2,
                                                          order_price=sell_price_2)
                sell_order_3 = kucoin_client.create_order(order_side="sell",
                                                          order_type="limit",
                                                          order_symbol=symbol,
                                                          order_size=sell_502525_size_2,
                                                          order_price=sell_price_3)
            except kucoin.APIException as exception:
                print(exception)
                current_status = str(exception) + " @ Limit Sell Orders"
                return

            sell_end_timestamp = time.time() * 1000

            buy_time = str(int(buy_end_timestamp - start_timestamp))
            sell_time = str(int(sell_end_timestamp - buy_end_timestamp))

            current_status = "Market buy @ {} in {}ms "\
                             "Limit sells @ {}, {} and {}  in {}ms".format(buy_price_precise,
                                                                           buy_time,
                                                                           sell_price_1,
                                                                           sell_price_2,
                                                                           sell_price_3,
                                                                           sell_time)
            sell_order_1_id = sell_order_1['orderId']
            sell_order_2_id = sell_order_2['orderId']
            sell_order_3_id = sell_order_3['orderId']
            sell_order_1 = kucoin_client.get_order(order_id=sell_order_1_id)
            sell_order_2 = kucoin_client.get_order(order_id=sell_order_2_id)
            sell_order_3 = kucoin_client.get_order(order_id=sell_order_3_id)

            print(buy_order)
            print("Executed in {}ms".format(buy_time))
            print(sell_order_1)
            print(sell_order_2)
            print(sell_order_3)
            print("Executed in {}ms".format(sell_time))

        return "Kucoin Trade Done."

    else:
        return "Trade Initiated Before"


@api.websocket("/api/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket):
    await websocket_manager.connect(websocket)
    previous_message = "previous_message"
    previous_symbol = "previous_symbol"
    previous_status = "previous status"
    try:
        while True:
            if current_message != previous_message or\
               current_symbol != previous_symbol or\
               current_status != previous_status:
                previous_message = current_message
                previous_symbol = current_symbol
                previous_status = current_status
                data = json.dumps({"message": current_message, "symbol": current_symbol, "status": current_status})
                await websocket_manager.send_personal_message(data, websocket)
                await asyncio.sleep(.25)
            else:
                await asyncio.sleep(.25)
    except ConnectionClosedError:
        websocket_manager.disconnect(websocket)


@api.get("/api/get_credentials", dependencies=[Depends(auth.implicit_scheme), Depends(auth.get_user)])
async def get_credentials(user: Auth0User = Security(auth.get_user)):
    access_token = await get_auth0_access_token()

    url = "https://botqoin.us.auth0.com/api/v2/users/{}".format(user.id)
    headers = {"Authorization": "Bearer {}".format(access_token),
               "content-type": "application/json"}
    response = requests.request("GET", url, headers=headers)
    return response.json()['user_metadata']


@api.post("/api/save_credentials", dependencies=[Depends(auth.implicit_scheme), Depends(auth.get_user)])
async def save_credentials(credentials: Credentials, user: Auth0User = Security(auth.get_user)):
    access_token = await get_auth0_access_token()

    url = "https://botqoin.us.auth0.com/api/v2/users/{}".format(user.id)
    data = json.dumps({"user_metadata": {"binance_api_key": credentials.binance_api_key,
                                         "binance_api_secret": credentials.binance_api_secret,
                                         "kucoin_api_key": credentials.kucoin_api_key,
                                         "kucoin_api_secret": credentials.kucoin_api_secret,
                                         "kucoin_api_passphrase": credentials.kucoin_api_passphrase}})
    headers = {"Authorization": "Bearer {}".format(access_token),
               "content-type": "application/json"}
    response = requests.request("PATCH", url, data=data, headers=headers)
    return response.json()


@api.get("/api/get_channels", dependencies=[Depends(auth.implicit_scheme), Depends(auth.get_user)])
async def get_channels():
    with open("/home/ubuntu/botqoin/backend/resources/channels.json") as channels_json:
        channels = json.load(channels_json)
    return channels


@api.post("/api/save_channels", dependencies=[Depends(auth.implicit_scheme), Depends(auth.get_user)])
async def save_channels(channels: Channels):
    with open("/home/ubuntu/botqoin/backend/resources/channels.json", "w") as channels_json:
        json.dump(json.loads(channels.json()), channels_json)
    return {"message": "success"}


@api.post('/api/manueltrade', dependencies=[Depends(auth.implicit_scheme), Depends(auth.get_user)])
async def manueltrade(trade_info: TradeInfo):
    global current_message, current_symbol
    symbol = trade_info.symbol
    if binance_trade_flag:
        symbol = symbol + trade_pair
    elif kucoin_trade_flag:
        symbol = symbol + "-" + trade_pair
    else:
        return {"message": "not running"}
    result = await initialize_trade(symbol)
    current_message = "MANUAL TRADE"
    current_symbol = symbol
    return {"message": result}


@api.post('/api/startup', dependencies=[Depends(auth.implicit_scheme), Depends(auth.get_user)])
async def startup(bot_info: BotInfo, user: Auth0User = Security(auth.get_user)):
    global profit_percentage_1, profit_percentage_2, profit_percentage_3, \
           sell_method, trade_pair, funds_quantity, \
           binance_trade_flag, kucoin_trade_flag, \
           current_status

    meta = await get_credentials(user=user)
    print(bot_info)

    trade_pair = bot_info.trade_pair
    sell_method = bot_info.sell_method
    profit_percentage_1 = bot_info.profit_percentage_1
    profit_percentage_2 = bot_info.profit_percentage_2
    profit_percentage_3 = bot_info.profit_percentage_3
    funds_quantity = bot_info.funds_quantity
    trade_pair = bot_info.trade_pair
    if bot_info.trade_platform == "Binance":
        binance_trade_flag = True
        await trader_start(meta)
    elif bot_info.trade_platform == "Kucoin":
        kucoin_trade_flag = True
        await trader_start(meta)
    else:
        return {"message": "failed"}

    current_status = "Listening for incoming messages, awaiting symbol fetch."

    return {"message": "success"}


@api.get("/api/closedown", dependencies=[Depends(auth.implicit_scheme), Depends(auth.get_user)])
async def closedown():
    global current_message, current_symbol, current_status, binance_trade_flag, kucoin_trade_flag

    binance_trade_flag = False
    kucoin_trade_flag = False

    await trader_stop()

    current_message = ""
    current_symbol = ""
    current_status = ""

    return {"message": "success"}


event_loop = asyncio.get_event_loop()
discord_task = event_loop.create_task(DiscordManager().start())
telegram_task = event_loop.create_task(TelegramManager().start())
