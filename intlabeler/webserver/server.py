"""This module contains WebServer class
    TODO DOC
"""

import asyncio
import datetime
import logging
import pathlib
from aiohttp import web
import json

import intlabeler.const.msg as const_msg
import intlabeler.const.payload as const_pl
import intlabeler.protocol.dto as dto


API_VERSION = 'v1.0'
API_URL = '/echo' + '/' + API_VERSION


class WebServer:
    """WebServer class doc TODO
    """
    def __init__(self, loop=None, host='127.0.0.1', port=8085, debugtoolbar=False):
        """ Parameters
            ----------
            loop : asyncio event loop
            host : string (optional, default is 127.0.0.1)
            port : int (optional, default is 8085)
            debugtoolbar : bool (default True) turn on aiohttp debugtoolbar
        """
        self._loop = loop
        self.host = host
        self.port = port
        self.log = logging.getLogger()
        self.app = web.Application(loop=self._loop)
        #states
        self.app['sockets'] = []
        self.app['solutions'] = {}
        #end of states
        if debugtoolbar:
            import aiohttp_debugtoolbar
            aiohttp_debugtoolbar.setup(self.app)
        #setup handlers
        self.app.router.add_routes([web.get(API_URL, self.wshandle)])
        static_folder="frontend/dist"
        self.app.router.add_static('/', static_folder, name='static', show_index=True)
        #here = pathlib.Path(__file__)

    async def start(self):
        web.run_app(self.app, host=self.host, port=self.port)
        print("Server started on http://%s:%s" % (self.host, self.port))

    #TODO move to specific module
    def list_tasks(self):
        return [t[const_pl.TASK_ID] for t in self.app["tasks"]]

    def client_msg(self, msg):
        res = dto.Message(const_msg.TYPE_ERROR, dto.Error("Nothing to do", None))
        try:
            data = json.loads(msg.data)
        except Exception as e:
            print(e)
        if not const_msg.TYPE in data:
            error_msg = "{} field reqired".format(const_msg.TYPE)
            return dto.Message(const_msg.TYPE_ERROR, dto.Error(error_msg, None))
        if data[const_msg.TYPE] == const_msg.TYPE_LIST:
            if len(self.app['tasks']) > 0:
                return dto.Message(const_msg.TYPE_LIST, self.list_tasks())
        return res

    async def wshandle(self, request):
        ws = web.WebSocketResponse()
        self.app["sockets"].append(ws)
        await ws.prepare(request)
        #first message
        #await ws.send_str(json.dumps({'command': 'tasks', 'user_name': '1'}))
        async for msg in ws:
            if msg.type == web.WSMsgType.text:
                self.app["solutions"]["1"] = msg.data
                reply = self.client_msg(msg)
                print(reply.to_dict())
                await ws.send_str(json.dumps(reply.to_dict()))
            elif msg.type == web.WSMsgType.binary:
                await ws.send_bytes(msg.data)
            elif msg.type == web.WSMsgType.close:
                break
        return ws

    async def ask_(self):
        end_time = self.app.loop.time() + 100.0
        while True:
            for ws in self.app['sockets']:
                await ws.send_str("Hello, {}".format("w"))

            if (self.app.loop.time() + 1.0) >= end_time:
                break
            if '1' in self.app['solutions']:
                if self.app['solutions']['1']:
                    res = self.app['solutions']['1']
                    self.app['solutions']['1'] = False
                    return res
            await asyncio.sleep(0.5)

    async def do_some_work(self, x):
        res = None
        try:
            res = await self.ask_()
        except Exception as e:
            print(e)
        return res


def run_fun(aiothread):
    #loop = aiothread.get_loop()
    timeout = 3000000
    coro = aiothread.server.do_some_work(4)
    future = aiothread.add_task(coro)
    #Make sure you wait for loop to start. Calling future.cancel() in main thread will cancel asyncio coroutine in background thread.
    try:
        result = future.result(timeout)
        print(result)
    except asyncio.TimeoutError:
        print('The coroutine took too long, cancelling the task')
        future.cancel()
    except Exception as exc:
        print('The coroutine raised an exception: {!r}'.format(exc))