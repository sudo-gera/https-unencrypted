from asyncio import transports
from pprint import pprint
import mitmproxy
import mitmproxy.http
import mitmproxy.flow
import json
import time
from traceback import *
import asyncio
import pickle
from serialize import *

name_to_queue={}

class Connection(asyncio.Protocol):
    async def start(self):
        loop = asyncio.get_running_loop()
        self.transport, self.protocol = await loop.create_datagram_endpoint(
        lambda: self,
        remote_addr=('127.0.0.1', 9999))

    def connection_made(self, transport) -> None:
        print('made')
        self.transport=transport

    def datagram_received(self, data, addr):
        data = loads(data,mitmproxy.http.Response)
        name, resp = data
        if name not in name_to_queue:
            name_to_queue[name]=asyncio.Queue()
        name_to_queue[name].put_nowait(resp)


    async def get_data(self,name):
        if name not in name_to_queue:
            name_to_queue[name]=asyncio.Queue()
        resp=await name_to_queue[name].get()
        del name_to_queue[name]
        return resp

    def send_data(self,req,name):
        self.transport.sendto(dumps([name,req]),('127.0.0.1',9999))

connection=None
lock=asyncio.Lock()

class mitm:
    async def request(self, flow:mitmproxy.http.HTTPFlow):
        global connection
        if connection==None:
            async with lock:
                if connection==None:
                    connection=Connection()
                    await connection.start()
        name=(int(time.time()*1000)&0xff_ff_ff_ff).to_bytes(4,'little')
        connection.send_data(flow.request,name)
        resp=await connection.get_data(name)
        if type(resp)==mitmproxy.http.Response:
            flow.response=resp
        else:
            flow.request.host='255.255.255.255'
    async def error(self, flow):
        print(time.asctime())
        print(time.time())
        print('error')
        pprint(flow)
        pprint(flow.get_state())
        time.sleep(0.1)
        print()
        print()

addons = [mitm()]


