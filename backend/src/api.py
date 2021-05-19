import asyncio
import datetime
import requests
from fastapi import FastAPI, WebSocket, Depends, Security
from fastapi_auth0 import Auth0, Auth0User
from fastapi.middleware.cors import CORSMiddleware
from websockets.exceptions import ConnectionClosedError, WebSocketException
from starlette.websockets import WebSocketDisconnect
from pydantic import BaseModel
from typing import List
from functools import cached_property
from cryptography.fernet import Fernet
from analyzer import message_analyzer
from binance.exceptions import *
from binance.enums import *
from binance.client import Client as BinanceClient
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


class Client:
    def __init__(self, websocket, binance_client, kucoin_client, discord_channels, telegram_channels,
                 profit_percentage_1, profit_percentage_2, profit_percentage_3,
                 funds_quantity, sell_method, trade_pair):

        self.is_active = True
        self.websocket = websocket
        self.binance_client = binance_client
        self.kucoin_client = kucoin_client
        self.discord_channels = discord_channels
        self.telegram_channels = telegram_channels
        self.profit_percentage_1 = profit_percentage_1
        self.profit_percentage_2 = profit_percentage_2
        self.profit_percentage_3 = profit_percentage_3
        self.funds_quantity = funds_quantity
        self.sell_method = sell_method
        self.trade_pair = trade_pair


class Credentials(BaseModel):
    binance_api_key: str
    binance_api_secret: str
    kucoin_api_key: str
    kucoin_api_secret: str
    kucoin_api_passphrase: str


class UserMetadata(BaseModel):
    credentials: Credentials
    discord_channels: dict
    telegram_channels: dict


class DiscordManager:
    def __init__(self):
        super().__init__()
        self.client.add_event_handler(self.on_message, 'MESSAGE_CREATE')

    @cached_property
    def client(self):
        return discord.Client(token="NTYyOTc0OTMzMDg1MzIzMjY0.YEPkaQ.qtaksxyYJQhNvWSLx2APvOZraCM")

    async def on_message(self, message):
        for client in clients:
            if client.is_active:
                if message.channel_id in client.discord_channels:
                    print("DC_TIMESTAMP: {} - LOCAL_TIMESTAMP: {}".format(message.timestamp, datetime.datetime.now()))
                    await self._handle_message(message.content, client)
                    try:
                        await self._handle_message(message.embeds[0].fields[0].value, client)
                    except:
                        pass
                    try:
                        await self._handle_message(message.embeds[0].description, client)
                    except:
                        pass
                    if client.is_active:
                        await client.websocket.send_json({"message": message.content,
                                                          "symbol": "------",
                                                          "status": "No symbol found, waiting for symbol scrape."})

    @staticmethod
    async def _handle_message(message, client):
        if client.is_active:
            symbol = message_analyzer(message, client.binance_client, client.kucoin_client, symbol_dictionary,
                                      client.trade_pair)
            if symbol != "":
                client.is_active = False
                await client.websocket.send_json({"message": message,
                                                  "symbol": symbol,
                                                  "status": "Symbol fetched, executing trade."})
                await initialize_trade(symbol, client)

    async def start(self):
        await self.client.start()


class TelegramManager:
    def __init__(self):
        super().__init__()
        self.client.add_event_handler(self.on_message, telethon.events.NewMessage)

    @cached_property
    def client(self):
        return telethon.TelegramClient('botQoin', 3112726, "15d793b32dc85708032b761fbaec12f6")

    @staticmethod
    async def on_message(event):
        for client in clients:
            if client.is_active:
                if event.chat.username in client.telegram_channels:
                    symbol = message_analyzer(event.message.message, client.binance_client,
                                              client.kucoin_client, symbol_dictionary,
                                              client.trade_pair)
                    if symbol != "":
                        client.is_active = False
                        await client.websocket.send_json({"message": event.message.message,
                                                          "symbol": symbol,
                                                          "status": "Symbol fetched, executing trade."})
                        await initialize_trade(symbol, client)
                    else:
                        await client.websocket.send_json({"message": event.message.message,
                                                          "symbol": "------",
                                                          "status": "No symbol found, waiting for symbol scrape."})

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

fernet_key = Fernet.generate_key()
fernet = Fernet(fernet_key)

clients = {}

symbol_dictionary = {}

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


async def _symbol_dictionary_refresher():
    while True:
        binance_response = requests.request("GET", "https://api.binance.com/api/v3/exchangeInfo")
        for symbol in binance_response.json()['symbols']:
            for filt in symbol['filters']:
                if 'PRICE_FILTER' in filt['filterType']:
                    symbol_dictionary[symbol['symbol']] = [str(float(filt['tickSize']))[-1],
                                                           str(symbol['baseAssetPrecision'])]
        kucoin_response = requests.request("GET", "https://api.kucoin.com/api/v1/symbols")
        for symbol in kucoin_response.json()['data']:
            price_digit = decimal.Decimal(symbol['priceIncrement'])
            price_precision_minus = price_digit.as_tuple().exponent
            price_precision = str(price_precision_minus).replace("-", "")
            base_digit = decimal.Decimal(symbol['baseIncrement'])
            base_precision_minus = base_digit.as_tuple().exponent
            base_precision = str(base_precision_minus).replace("-", "")
            symbol_dictionary[symbol['symbol']] = [price_precision, base_precision]

        await asyncio.sleep(86400)


async def initialize_trade(symbol, user_client):

    binance_client = user_client.binance_client
    kucoin_client = user_client.kucoin_client
    profit_percentage_1 = user_client.profit_percentage_1
    profit_percentage_2 = user_client.profit_percentage_2
    profit_percentage_3 = user_client.profit_percentage_3
    funds_quantity = user_client.funds_quantity
    sell_method = user_client.sell_method

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

    trade_initialize_time = datetime.datetime.now()

    start_timestamp = time.time() * 1000

    if binance_client is not None:
        try:
            buy_order = binance_client.create_order(
                symbol=symbol,
                side=SIDE_BUY,
                type=ORDER_TYPE_MARKET,
                quoteOrderQty=funds_quantity)
            print(buy_order)
        except (BinanceRequestException, BinanceAPIException) as exception:
            exception = str(exception) + " @ Market Buy Order"
            print(exception)
            await user_client.websocket.send_json({"status": exception})
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
            except (BinanceRequestException, BinanceAPIException) as exception:
                exception = str(exception) + " @ Sell Order"
                print(exception)
                await user_client.websocket.send_json({"status": exception})
                return

            sell_end_timestamp = time.time() * 1000

            buy_time = str(int(buy_end_timestamp - start_timestamp))
            sell_time = str(int(sell_end_timestamp - buy_end_timestamp))

            result = "Market buy @ {} in {}ms -- Limit sell @ {} in {}ms".format(buy_price_precise,
                                                                                 buy_time,
                                                                                 sell_price_1,
                                                                                 sell_time)
            await user_client.websocket.send_json({"status": result})

            print(sell_order)

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
            except (BinanceRequestException, BinanceAPIException) as exception:
                exception = str(exception) + " @ Sell Orders"
                print(exception)
                await user_client.websocket.send_json({"status": exception})
                return

            sell_end_timestamp = time.time() * 1000

            buy_time = str(int(buy_end_timestamp - start_timestamp))
            sell_time = str(int(sell_end_timestamp - buy_end_timestamp))

            result = "Market buy @ {} in {}ms -- Limit sells @ {} and {} in {}ms".format(buy_price_precise,
                                                                                         buy_time,
                                                                                         sell_price_1,
                                                                                         sell_price_2,
                                                                                         sell_time)
            await user_client.websocket.send_json({"status": result})

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
            except (BinanceRequestException, BinanceAPIException) as exception:
                exception = str(exception) + " @ Sell Orders"
                print(exception)
                await user_client.websocket.send_json({"status": exception})
                return

            sell_end_timestamp = time.time() * 1000

            buy_time = str(int(buy_end_timestamp - start_timestamp))
            sell_time = str(int(sell_end_timestamp - buy_end_timestamp))

            result = "Market buy @ {} in {}ms -- Limit sells @ {}, {} and {} in {}ms".format(buy_price_precise,
                                                                                             buy_time,
                                                                                             sell_price_1,
                                                                                             sell_price_2,
                                                                                             sell_price_3,
                                                                                             sell_time)
            await user_client.websocket.send_json({"status": result})

            print(sell_order_1)
            print(sell_order_2)
            print(sell_order_3)

    if kucoin_client is not None:

        try:
            buy_order = kucoin_client.create_order(order_side="buy",
                                                   order_type="market",
                                                   order_symbol=symbol,
                                                   order_funds=funds_quantity,)
        except kucoin.APIException as exception:
            exception = str(exception) + " @ Market Buy Order"
            print(exception)
            await user_client.websocket.send_json({"status": exception})
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
                exception = str(exception) + " @ Limit Sell Order"
                print(exception)
                await user_client.websocket.send_json({"status": exception})
                return

            sell_end_timestamp = time.time() * 1000

            buy_time = str(int(buy_end_timestamp - start_timestamp))
            sell_time = str(int(sell_end_timestamp - buy_end_timestamp))

            result = "Market buy @ {} in {}ms - Limit sell @ {} in {}ms - Trade Start: {}".format(
                                                                                           buy_price_precise,
                                                                                           buy_time,
                                                                                           sell_price_1,
                                                                                           sell_time,
                                                                                           trade_initialize_time)
            await user_client.websocket.send_json({"status": result})

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
                exception = str(exception) + " @ Limit Sell Orders"
                print(exception)
                await user_client.websocket.send_json({"status": exception})
                return

            sell_end_timestamp = time.time() * 1000

            buy_time = str(int(buy_end_timestamp - start_timestamp))
            sell_time = str(int(sell_end_timestamp - buy_end_timestamp))

            result = "Market buy @ {} in {}ms - Limit sells @ {} and {} in {}ms - Trade Start: {}".format(
                                                                                               buy_price_precise,
                                                                                               buy_time,
                                                                                               sell_price_1,
                                                                                               sell_price_2,
                                                                                               sell_time,
                                                                                               trade_initialize_time)
            await user_client.websocket.send_json({"status": result})

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
                exception = str(exception) + " @ Limit Sell Orders"
                print(exception)
                await user_client.websocket.send_json({"status": exception})
                return

            sell_end_timestamp = time.time() * 1000

            buy_time = str(int(buy_end_timestamp - start_timestamp))
            sell_time = str(int(sell_end_timestamp - buy_end_timestamp))

            result = "Market buy @ {} in {}ms - Limit sells @ {}, {} and {}  in {}ms - Trade Start: {}".format(
                                                                                                buy_price_precise,
                                                                                                buy_time,
                                                                                                sell_price_1,
                                                                                                sell_price_2,
                                                                                                sell_price_3,
                                                                                                sell_time,
                                                                                                trade_initialize_time)
            await user_client.websocket.send_json({"status": result})

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


async def _get_auth0_access_token():
    url = "https://botqoin.us.auth0.com/oauth/token"
    data = json.dumps({"client_id": "c3gy7WhgX6HIjdHzTWdRn6vQ8BIz2iIg",
                       "client_secret": "HodmVihOGeuOq_8jsgcAWzaT4H4v0SYF5FIuimv-gJsTBuzUcmc2JvQWUnwzNMOj",
                       "audience": "https://botqoin.us.auth0.com/api/v2/",
                       "grant_type": "client_credentials"})
    headers = {"content-type": "application/json"}
    response = requests.request("POST", url, data=data, headers=headers)
    return response.json()['access_token']


async def _generate_exchange_client(credentials, trade_platform):
    if trade_platform == "Binance":
        client = BinanceClient(credentials['binance_api_key'],
                               credentials['binance_api_secret'])

    elif trade_platform == "Kucoin":
        client = kucoin.Client(credentials['kucoin_api_key'],
                               credentials['kucoin_api_secret'],
                               credentials['kucoin_api_passphrase'])
    else:
        return

    return client


async def _handle_new_client(bot_settings, websocket, user_id):

    user_metadata = await get_user_metadata(user_id=user_id)

    credentials: dict = user_metadata['credentials']
    discord_channels: dict = user_metadata['discord_channels']
    telegram_channels: dict = user_metadata['telegram_channels']

    trade_platform = bot_settings['trade_platform']
    trade_pair = bot_settings['trade_pair']
    funds_quantity = bot_settings['funds_quantity']
    sell_method = bot_settings['sell_method']
    profit_percentage_1 = bot_settings['profit_percentage_1']
    profit_percentage_2 = bot_settings['profit_percentage_2']
    profit_percentage_3 = bot_settings['profit_percentage_3']

    exchange_client = await _generate_exchange_client(credentials, trade_platform)
    if trade_platform == "Binance":
        new_client = Client(websocket, exchange_client, None, discord_channels, telegram_channels,
                            profit_percentage_1, profit_percentage_2, profit_percentage_3,
                            funds_quantity, sell_method, trade_pair)
    elif trade_platform == "Kucoin":
        new_client = Client(websocket, None, exchange_client, discord_channels, telegram_channels,
                            profit_percentage_1, profit_percentage_2, profit_percentage_3,
                            funds_quantity, sell_method, trade_pair)
    else:
        return
    clients[new_client] = user_id
    print("A NEW CLIENT HAS BEEN GENERATED")
    print(clients)


async def _handle_metadata_request(method: str, user_id: str, user_metadata: UserMetadata = None):
    access_token = await _get_auth0_access_token()
    url = "https://botqoin.us.auth0.com/api/v2/users/{}".format(user_id)
    headers = {"Authorization": "Bearer {}".format(access_token),
               "content-type": "application/json"}
    if method == "GET":
        response = requests.request("GET", url, headers=headers)
        return response.json()['user_metadata']
    elif method == "POST":
        data = json.dumps({"user_metadata": {"credentials": dict(user_metadata.credentials),
                                             "discord_channels": user_metadata.discord_channels,
                                             "telegram_channels": user_metadata.telegram_channels}})
        response = requests.request("PATCH", url, data=data, headers=headers)
        return response.json()
    else:
        return "UNSUPPORTED REQUEST TYPE"


@api.websocket("/api/websocket/bot/{ticket}")
async def websocket_bot(websocket: WebSocket, ticket):
    await websocket_manager.connect(websocket)
    ticket = ticket.encode()
    user_id = fernet.decrypt(ticket).decode()
    try:
        while True:
            data = await websocket.receive_json()
            if data['method'] == "SUBSCRIBE":
                bot_params = data['params']
                await _handle_new_client(bot_params, websocket, user_id)
                await websocket.send_json({"status": "Bot has started, awaiting for symbol scrape."})
                await websocket.send_json({"signal": "READY"})
            elif data['method'] == "UNSUBSCRIBE":
                for client, id in list(clients.items()):
                    if id == user_id:
                        del clients[client]
    except (ConnectionClosedError, WebSocketException, WebSocketDisconnect):
        websocket_manager.disconnect(websocket)
        for client, id in list(clients.items()):
            if id == user_id:
                del clients[client]


@api.get("/api/user/ticket", dependencies=[Depends(auth.implicit_scheme), Depends(auth.get_user)])
async def get_ticket(user: Auth0User = Security(auth.get_user)):
    return fernet.encrypt(user.id.encode())


@api.get("/api/user/metadata", dependencies=[Depends(auth.implicit_scheme), Depends(auth.get_user)])
async def get_user_metadata(user: Auth0User = Security(auth.get_user), user_id: str = None):
    if user_id is not None:
        return await _handle_metadata_request("GET", user_id)
    else:
        return await _handle_metadata_request("GET", user.id)


@api.post("/api/user/metadata", dependencies=[Depends(auth.implicit_scheme), Depends(auth.get_user)])
async def post_user_metadata(user: Auth0User = Security(auth.get_user), user_metadata: UserMetadata = None):
    return await _handle_metadata_request("POST", user.id, user_metadata)


event_loop = asyncio.get_event_loop()
discord_task = event_loop.create_task(DiscordManager().start())
telegram_task = event_loop.create_task(TelegramManager().start())
refresher_task = event_loop.create_task(_symbol_dictionary_refresher())
