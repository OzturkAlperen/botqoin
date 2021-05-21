import json
import hmac
import hashlib
import base64
import time
import websockets
import aiohttp


class Client:
    def __init__(self, key: str = None, secret: str = None, passphrase: str = None):
        self.key = key
        self.secret = secret
        if passphrase:
            self.passphrase = base64.b64encode(hmac.new(secret.encode('utf-8'),
                                                        passphrase.encode('utf-8'),
                                                        hashlib.sha256).digest()).decode("utf8")
        self.session = None

    async def close(self):
        await self.session.close()

    async def open(self):
        self.session = await self._init_session()

    async def _init_session(self):
        headers = {'Accept': 'application/json',
                   'User-Agent': 'botqoin',
                   'Content-Type': 'application/json',
                   'KC-API-KEY': self.key,
                   'KC-API-PASSPHRASE': self.passphrase,
                   "KC-API-KEY-VERSION": "2"}
        return aiohttp.ClientSession(headers=headers)

    async def _create_signature(self, method, endpoint, data):
        now = int(time.time() * 1000)
        if data:
            string_to_sign = str(now) + method + endpoint + data
        else:
            string_to_sign = str(now) + method + endpoint

        signature = base64.b64encode(hmac.new(self.secret.encode('utf-8'),
                                              string_to_sign.encode('utf-8'),
                                              hashlib.sha256).digest()).decode("utf8")
        return now, signature

    async def _make_request(self, method, endpoint, **kwargs):
        url = "https://api.kucoin.com{}".format(endpoint)
        data = {}
        for k, v in kwargs.items():
            data[k] = v
        data_json = json.dumps(data, separators=(',', ':'), ensure_ascii=False)
        now, signature = await self._create_signature(method, endpoint, data_json)
        headers = {
            "KC-API-TIMESTAMP": str(now),
            "KC-API-SIGN": signature,
        }
        async with getattr(self.session, method.lower())(url, headers=headers, data=data_json) as response:
            return await self._process_response(response)

    @staticmethod
    async def _process_response(response):
        if not str(response.status).startswith('2'):
            raise KucoinAPIException(response, None)
        try:
            response_json = await response.json()

            if 'code' in response_json and response_json['code'] != "200000":
                raise KucoinAPIException(response, response_json)

            if 'success' in response_json and not response_json['success']:
                raise KucoinAPIException(response, response_json)

            if 'data' in response_json:
                return response_json['data']

        except ValueError:
            return "INVALID RESPONSE"

    async def create_order(self,
                           order_side: str,
                           order_type: str,
                           order_symbol: str,
                           order_funds: str = None,
                           order_size: str = None,
                           order_price: str = None,
                           order_clientoid: str = None):
        if order_clientoid is not None:
            clientoid = order_clientoid
        else:
            clientoid = str(int(time.time() * 1000)) + order_side + order_type + order_symbol.replace("-", "")

        if order_type == "market":
            if order_funds is not None and order_size is None:
                return await self._make_request('POST', '/api/v1/orders',
                                                clientOid=clientoid,
                                                side=order_side,
                                                type=order_type,
                                                symbol=order_symbol,
                                                funds=order_funds)
            elif order_funds is None and order_size is not None:
                return await self._make_request('POST', '/api/v1/orders',
                                                clientOid=clientoid,
                                                side=order_side,
                                                type=order_type,
                                                symbol=order_symbol,
                                                size=order_size)
            else:
                return "Error @ order_size/order_funds"
        elif order_type == "limit":
            if order_funds is not None and order_size is None:
                return await self._make_request('POST', '/api/v1/orders',
                                                clientOid=clientoid,
                                                side=order_side,
                                                type=order_type,
                                                symbol=order_symbol,
                                                funds=order_funds,
                                                price=order_price)
            elif order_funds is None and order_size is not None:
                return await self._make_request('POST', '/api/v1/orders',
                                                clientOid=clientoid,
                                                side=order_side,
                                                type=order_type,
                                                symbol=order_symbol,
                                                funds=order_funds,
                                                size=order_size,
                                                price=order_price)
            else:
                return "Error @ order_size/order_funds"
        else:
            return "Error @ order_type"

    async def cancel_order(self, order_id: str = None, order_clientoid: str = None):
        if order_id is not None:
            return await self._make_request('DELETE', '/api/v1/orders/{}'.format(order_id))
        elif order_clientoid is not None:
            return await self._make_request('DELETE', '/api/v1/order/client-order/{}'.format(order_clientoid))
        else:
            return "Error -> Provide either order_id or order_clientoid"

    async def get_order(self, order_id: str = None, order_clientoid: str = None):
        if order_id is not None:
            return await self._make_request('GET', '/api/v1/orders/{}'.format(order_id))
        elif order_clientoid is not None:
            return await self._make_request('GET', '/api/v1/order/client-order/{}'.format(order_clientoid))
        else:
            return "Error -> Provide either order_id or order_clientoid"

    async def get_symbols(self):
        return await self._make_request('GET', '/api/v1/symbols')


class KucoinAPIException(Exception):
    def __init__(self, response, response_json):

        self.code = 'Unknown'
        self.message = 'Unknown'

        if response_json is not None:
            self.response_json = response_json
            if 'error' in self.response_json:
                self.message = response['error']
            if 'msg' in self.response_json:
                self.message = self.response_json['msg']
            if 'message' in self.response_json and self.response_json['message'] != 'No message available':
                self.message += ' - {}'.format(self.response_json['message'])
            if 'code' in self.response_json:
                self.code = self.response_json['code']
            if 'data' in self.response_json:
                try:
                    self.message += " " + json.dumps(self.response_json['data'])
                except ValueError:
                    pass
        else:
            self.message = response.content

        self.status_code = response.status
        self.response = response
        self.request = getattr(response, 'request', None)

    def __str__(self):
        return 'KucoinException {} -> {}'.format(self.code, self.message)


class WebSockets:
    def __init__(self, client):
        super().__init__()
        self.client = client
        self.data = self._get_public_token()
        self.token = self.data['token']
        self.servers = self.data['instanceServers']
        self.server = self.servers[0]
        self.endpoint = self.server['endpoint']
        self.interval = self.server['pingInterval']
        self.timeout = self.server['pingTimeout']
        self.now = str(int(time.time() * 1000))
        self.url = "{0}?token={1}&[connectId={2}]".format(self.endpoint, self.token, self.now)

    def _get_public_token(self):
        return self.client.make_request('post', '/api/v1/bullet-public')

    async def subscribe(self, topic, callback):
        async with websockets.connect(self.url) as websocket:
            now = str(int(time.time() * 1000))
            data = {"id": now,
                    "type": "subscribe",
                    "topic": topic,
                    "privateChannel": False,
                    "response": True}
            data_json = json.dumps(data)
            await websocket.send(data_json)
            async for message in websocket:
                await callback(message)
