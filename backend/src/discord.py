import asyncio
import zlib
import json
import websockets
from websockets import ConnectionClosedError
from munch import munchify


class AuthorizationError(BaseException):
    def __init__(self, error=None):
        self.error = error
        if str(self.error.code) == "4004":
            self.reason = str(self.error.reason)

    def __str__(self):
        if self.error is None:
            return "Authentication failed"
        return self.error.reason


class Client:
    def __init__(self, token: str):

        self.token = token
        self.api_version = 9

        self.user_handlers = {}
        self.sequence = None

        self.websocket_url = 'wss://gateway.discord.gg/?encoding=json&v='+str(self.api_version)+'&compress=zlib-stream'

        self.ZLIB_SUFFIX = b'\x00\x00\xff\xff'
        self.buffer = bytearray()
        self.inflator = zlib.decompressobj()

    def add_event_handler(self, callback, event: str):
        self.user_handlers[callback] = event

    async def start(self):
        try:
            async with websockets.connect(self.websocket_url) as websocket:
                while True:
                    stream = await websocket.recv()
                    payload = await self._decompress_stream(stream)
                    await self._handle_payload(payload, websocket)
        except ConnectionClosedError as error:
            raise AuthorizationError(error)

    async def _authorize(self, websocket):
        payload = json.dumps({
            "op": 2,
            "d": {
                "token": self.token,
                "capabilities": 61,
                "properties": {
                    "$os": "linux",
                    "$browser": "botqoin",
                    "$device": "amazon_ec2"
                }
            },
            "presence": {
                "status": "online",
                "since": 0,
                "activities": [],
                "afk": False
            },
            "compress": False,
        })
        await websocket.send(payload)

    async def _decompress_stream(self, stream):
        self.buffer.extend(stream)
        if len(stream) < 4 or stream[-4:] != self.ZLIB_SUFFIX:
            return
        payload = json.loads(self.inflator.decompress(self.buffer).decode())
        self.buffer = bytearray()
        return payload

    async def _handle_payload(self, payload, websocket):
        if payload['s'] != 0 and None:
            self.sequence = payload['s']

        if payload['op'] == 10:
            heartbeat_interval = payload['d']['heartbeat_interval']
            asyncio.get_event_loop().create_task(self._i_am_alive(websocket, heartbeat_interval))
            await self._authorize(websocket)

        elif payload['op'] == 1:
            payload = json.dumps({
                "op": 1,
                "d": self.sequence
            })
            await websocket.send(payload)

        elif payload['op'] == 6:
            print(payload)

        elif payload['op'] == 7:
            print(payload)

        elif payload['op'] == 11:
            # HEARTBEAT ACK
            pass

        elif payload['op'] == 9:
            raise AuthorizationError

        else:
            for callback, event in self.user_handlers.items():
                if event == payload['t']:
                    _event_obj_struct = munchify(payload['d'])
                    await callback(_event_obj_struct)

        if payload['t'] == ['HELLO']:
            print(payload)

        if payload['t'] == ['READY']:
            print(payload)

        if payload['t'] == ['RESUME']:
            print(payload)

        if payload['t'] == ['RECONNECT']:
            print(payload)

    async def _i_am_alive(self, websocket, interval: int):
        while True:
            interval_in_seconds = interval / 1000.0
            await asyncio.sleep(interval_in_seconds)
            payload = {
                "op": 1,
                "d": self.sequence
            }
            await websocket.send(json.dumps(payload))
