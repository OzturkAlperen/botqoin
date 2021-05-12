import json
import hmac
import hashlib
import base64
import time
import requests
import websockets


class Client:
    def __init__(self, key: str = None, secret: str = None, passphrase: str = None):
        self.key = key
        self.secret = secret
        if passphrase:
            self.passphrase = base64.b64encode(hmac.new(secret.encode('utf-8'),
                                                        passphrase.encode('utf-8'),
                                                        hashlib.sha256).digest())
            self.session = self._init_session()

    def _init_session(self):
        session = requests.session()
        headers = {'Accept': 'application/json',
                   'User-Agent': 'botqoin',
                   'Content-Type': 'application/json',
                   'KC-API-KEY': self.key,
                   'KC-API-PASSPHRASE': self.passphrase,
                   "KC-API-KEY-VERSION": "2"}
        session.headers.update(headers)
        return session

    def _create_signature(self, method, endpoint, data):
        now = int(time.time() * 1000)
        if data:
            string_to_sign = str(now) + method + endpoint + data
        else:
            string_to_sign = str(now) + method + endpoint
        signature = base64.b64encode(hmac.new(self.secret.encode('utf-8'),
                                              string_to_sign.encode('utf-8'),
                                              hashlib.sha256).digest())
        return now, signature

    def _make_request(self, method, endpoint, **kwargs):
        url = "https://api.kucoin.com{}".format(endpoint)
        data = {}
        for k, v in kwargs.items():
            data[k] = v
        data_json = json.dumps(data, separators=(',', ':'), ensure_ascii=False)
        now, signature = self._create_signature(method, endpoint, data_json)
        headers = {
            "KC-API-TIMESTAMP": str(now),
            "KC-API-SIGN": signature,
        }
        try:
            return self._process_response(getattr(self.session, method.lower())(url, headers=headers, data=data_json))
        except requests.exceptions.RequestException as exception:
            return exception

    @staticmethod
    def _process_response(response):

        if not str(response.status_code).startswith('2'):
            raise APIException(response)
        try:
            response_json = response.json()

            if 'code' in response_json and response_json['code'] != "200000":
                raise APIException(response)

            if 'success' in response_json and not response_json['success']:
                raise APIException(response)

            if 'data' in response_json:
                return response_json['data']

        except ValueError:
            raise APIException(request_exception='Invalid Response: %s' % response.text, response=response)

    def create_order(self,
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
                return self._make_request('POST', '/api/v1/orders',
                                          clientOid=clientoid,
                                          side=order_side,
                                          type=order_type,
                                          symbol=order_symbol,
                                          funds=order_funds)
            elif order_funds is None and order_size is not None:
                return self._make_request('POST', '/api/v1/orders',
                                          clientOid=clientoid,
                                          side=order_side,
                                          type=order_type,
                                          symbol=order_symbol,
                                          size=order_size)
            else:
                return "Error @ order_size/order_funds"
        elif order_type == "limit":
            if order_funds is not None and order_size is None:
                return self._make_request('POST', '/api/v1/orders',
                                          clientOid=clientoid,
                                          side=order_side,
                                          type=order_type,
                                          symbol=order_symbol,
                                          funds=order_funds,
                                          price=order_price)
            elif order_funds is None and order_size is not None:
                return self._make_request('POST', '/api/v1/orders',
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

    def cancel_order(self, order_id: str = None, order_clientoid: str = None):
        if order_id is not None:
            return self._make_request('DELETE', '/api/v1/orders/{}'.format(order_id))
        elif order_clientoid is not None:
            return self._make_request('DELETE', '/api/v1/order/client-order/{}'.format(order_clientoid))
        else:
            return "Error -> Provide either order_id or order_clientoid"

    def get_order(self, order_id: str = None, order_clientoid: str = None):
        if order_id is not None:
            return self._make_request('GET', '/api/v1/orders/{}'.format(order_id))
        elif order_clientoid is not None:
            return self._make_request('GET', '/api/v1/order/client-order/{}'.format(order_clientoid))
        else:
            return "Error -> Provide either order_id or order_clientoid"

    def get_symbols(self):
        return self._make_request('GET', '/api/v1/symbols')


class APIException(Exception):
    def __init__(self, response, request_exception=None):

        self.request_exception = request_exception
        self.code = 'Unknown'
        self.message = 'Unknown'

        try:
            response_json = response.json()
        except ValueError:
            self.message = response.content
        else:
            if 'error' in response_json:
                self.message = response['error']
            if 'msg' in response_json:
                self.message = response_json['msg']
            if 'message' in response_json and response_json['message'] != 'No message available':
                self.message += ' - {}'.format(response_json['message'])
            if 'code' in response_json:
                self.code = response_json['code']
            if 'data' in response_json:
                try:
                    self.message += " " + json.dumps(response_json['data'])
                except ValueError:
                    pass

        self.status_code = response.status_code
        self.response = response
        self.request = getattr(response, 'request', None)

    def __str__(self):
        if self.request_exception is not None:
            return 'KucoinException: {}'.format(self.request_exception)
        else:
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
