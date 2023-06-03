import multiprocessing
from multiprocessing import Process

import socketio
from aiohttp import web
from aiohttp.web_runner import GracefulExit

multiprocessing.set_start_method("fork")



class EventEmitter:

    __instance = None

    def __init__(self):
        if EventEmitter.__instance is not None:
            raise NotImplementedError()
        else:
            self.sio = socketio.AsyncServer(async_mode="aiohttp", async_handlers=True,cors_allowed_origins="*")
            self.app = web.Application()
            self.sio.attach(self.app)
            EventEmitter.__instance = self

    @staticmethod
    def get_instance():
        if EventEmitter.__instance is None:
            EventEmitter()
        return EventEmitter.__instance

    async def init_app(self,task):
        async def wrap():
            await task()
            raise GracefulExit()
        self.sio.start_background_task(wrap)
        return self.app

    def start(self,task):
        self.thread = Process(target=web.run_app(self.init_app(task), host="127.0.0.1", port=5000))
        self.thread.start()

