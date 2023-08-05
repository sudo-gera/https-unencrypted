import pickle
import base64
from pprint import pprint
import mitmproxy.http
def request_dumps(req:mitmproxy.http.Request)->bytes:
    return pickle.dumps(req.get_state())

def response_dumps(req:mitmproxy.http.Response)->bytes:
    return pickle.dumps(req.get_state())

def request_loads(data:bytes)->mitmproxy.http.Request:
    data=pickle.loads(data)
    r=mitmproxy.http.Request(**data)
    r.set_state(data)
    return r

def response_loads(data:bytes)->mitmproxy.http.Response:
    data=pickle.loads(data)
    r=mitmproxy.http.Response(**data)
    r.set_state(data)
    return r



def dumps(tflow:tuple[bytes,mitmproxy.http.Request|mitmproxy.http.Response|None])->bytes:
    name,flow=tflow
    if isinstance(flow,mitmproxy.http.Request):
        return name+request_dumps(flow)
    if isinstance(flow,mitmproxy.http.Response):
        return name+response_dumps(flow)
    if flow is None:
        return name
    raise RuntimeError

def loads(data:bytes,t:type):
    name, flow=data[:4],data[4:]
    if not flow:
        return (name,None)
    if t==mitmproxy.http.Response:
        return (name,response_loads(flow))
    if t==mitmproxy.http.Request:
        return (name,request_loads(flow))
    raise RuntimeError

def encode(data:bytes)->str:
    return '_'+base64.b64encode(data).decode().replace('+','-').replace('/','_')

def decode(data:bytes|str)->bytes:
    if type(data)==bytes:
        data=data.decode()
    if data[0]!='_':
        return None
    data=data[1:]
    return base64.b64decode(data.replace('-','+').replace('_','/'))
