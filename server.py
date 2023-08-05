import asyncio
import aiohttp
import base64
import pickle
from serialize import *

class connection:
    def __init__(self, session):
        self.session=session

    def connection_made(self, transport):
        print('made')
        self.transport = transport

    def datagram_received(self, data, addr):
        asyncio.create_task(self.datagram_received_async(data,addr))
    
    async def datagram_received_async(self, data, addr):
        name, req = loads(data,mitmproxy.http.Request)
        print('recv',len(data))
        session=self.session
        data=encode(data)
        async with session.get('http://255.255.255.255/'+data, proxy='http://127.0.0.1:9090') as resp:
            data=await resp.read()
            data=decode(data)
            if data is None:
                print('send error')
                self.transport.sendto(dumps((name,None)),addr)
            print('send',len(data))
            self.transport.sendto(data,addr)

async def main():
    async with aiohttp.ClientSession(trust_env=True) as session:
        loop = asyncio.get_running_loop()
        transport, protocol = await loop.create_datagram_endpoint(
            lambda: connection(session),
            local_addr=('127.0.0.1', 9999))


        try:
            await asyncio.Queue().get()
        finally:
            transport.close()


asyncio.run(main())
