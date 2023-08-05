from pprint import pprint
import mitmproxy
import mitmproxy.http
import json
import time
from traceback import *
import asyncio
import pickle
import base64
from serialize import *

class mitm:
    async def request(self, flow:mitmproxy.http.HTTPFlow):
        data=flow.request.path[1:]
        data=decode(data)
        name, req = loads(data,mitmproxy.http.Request)
        flow.request=req
        flow.name=name
    async def response(self, flow:mitmproxy.http.HTTPFlow):
        name, resp = flow.name, flow.response
        data=dumps([name, resp])
        data=encode(data)
        flow.response=flow.response.make(200,data)
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
