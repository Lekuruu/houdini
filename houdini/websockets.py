from websockets.exceptions import ConnectionClosed
from websockets import WebSocketClientProtocol
from websockets.protocol import State
from websockets.server import serve
from houdini.penguin import Penguin

import asyncio
import logging
import ssl

class WebsocketWriter:
    """Replacement for the `StreamWriter` class in asyncio"""
    def __init__(self, websocket: WebSocketClientProtocol):
        self.websocket = websocket
        self.stack = b''

    def write(self, data: bytes) -> None:
        self.stack += data

    async def drain(self) -> None:
        if not self.stack:
            return

        await self.websocket.send(self.stack)
        self.stack = b''

    def close(self) -> None:
        asyncio.create_task(self.websocket.close())

    def is_closing(self) -> bool:
        return self.websocket.state == State.CLOSING
    
    def get_extra_info(self, name: str, default=None):
        if name == 'peername':
            return resolve_ip_address(self.websocket)
        return default

class WebsocketReader:
    """Replacement for the `StreamReader` class in asyncio"""
    def __init__(self, websocket: WebSocketClientProtocol):
        self.websocket = websocket
        self.stack = b''

    async def readuntil(self, separator: bytes) -> bytes:
        try:
            # Check if stack has the separator
            if separator in self.stack:
                index = self.stack.index(separator)
                data = self.stack[:index + len(separator)]
                self.stack = self.stack[index + len(separator):]
                return data

            # Read from the websocket until the separator is found
            self.stack += await self.websocket.recv()
            return await self.readuntil(separator)
        except ConnectionClosed:
            raise ConnectionResetError()

def resolve_ip_address(websocket: WebSocketClientProtocol) -> str:
    headers = websocket.request_headers

    if 'CF-Connecting-IP' in headers:
        return headers['CF-Connecting-IP']

    if 'X-Real-IP' in headers:
        return headers['X-Real-IP'].strip()
    
    if 'X-Forwarded-For' in headers:
        return headers['X-Forwarded-For'].split(',')[0]

    return websocket.remote_address[0]

async def websocket_handler(factory, websocket: WebSocketClientProtocol, path: str):
    reader = WebsocketReader(websocket)
    writer = WebsocketWriter(websocket)
    penguin = Penguin(factory, reader, writer)
    await penguin.run()

def handler_wrapper(factory):
    return lambda websocket, path: websocket_handler(factory, websocket, path)

async def websocket_listener(factory) -> None:
    handler = handler_wrapper(factory)
    logger = logging.getLogger(__name__)

    host = factory.config.websocket_host
    port = factory.config.websocket_port
    ssl_context = None

    if factory.config.websocket_certificate_path:
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ssl_context.load_cert_chain(factory.config.websocket_certificate_path)

    async with serve(handler, host, port, ssl=ssl_context):
        logger.info(f'Websocket server listening on {host}:{port}')
        await asyncio.Future()
