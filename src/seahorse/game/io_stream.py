from __future__ import annotations

import asyncio
import functools
import json
from collections import deque
from typing import Callable

import socketio
from aiohttp import web

from seahorse.game.action import Action


class EventSlave:

    def activate(self,identifier:str=None) -> None:
        self.sio = socketio.AsyncClient()
        self.connected = False
        self.identifier = identifier
        self.incoming_plays_queue = deque()

        @self.sio.event()
        async def connect():
            self.connected = True
            if self.identifier is not None:
                await self.sio.emit("identify",json.dumps(self.__dict__,default=lambda _:"bob"))

        @self.sio.event()
        def disconnect():
            self.connected = False

        @self.sio.on("play")
        # TODO sid check
        def handle_play(*_):
            self.incoming_plays_queue.appendleft(_)

        @self.sio.on("turn")
        def handle_turn(*_):
            #print("turn")
            pass

    async def wait_for_next_play(self) -> Action:
        while not len(self.incoming_plays_queue):
            await asyncio.sleep(1)
        return self.incoming_plays_queue.pop()

    async def listen(self,*,keep_alive:bool) -> None:
        if not self.connected:
            await self.sio.connect("http://localhost:8080")
        if keep_alive:
            while self.connected:
                await asyncio.sleep(1)

def event_emitting(label:str):
    def meta_wrapper(fun: Callable):
        @functools.wraps(fun)
        async def wrapper(self:EventSlave,*args,**kwargs):
            out = fun(self,*args, **kwargs)
            # TODO: fix bob
            await self.sio.emit(label,json.dumps(out.__dict__,default=lambda _:"bob"))
            return out
        return wrapper
    return meta_wrapper

def remote_action(label:str):
    def meta_wrapper(fun: Callable):
        @functools.wraps(fun)
        async def wrapper(self:EventSlave,**_):
            # TODO: fix bob
            await EventMaster.get_instance().sio.emit(label,"prout",to=self.sid)
            #print("waiting for next play")
            out = await self.wait_for_next_play()
            return out
        return wrapper
    return meta_wrapper


class EventMaster:
    """
    Singleton for emitting events

    Attributes:


    Raises:
        NotImplementedError: when trying to initialize more than once

    """

    __instance = None

    @staticmethod
    def get_instance(n_clients:int=1) -> EventMaster:
        """Gets the instance object

        Args:
            n_clients (int, optional): the number of clients the instance is supposed to be listening, *ignored* if already initialized. Defaults to 1.

        Returns:
            object: _description_
        """
        if EventMaster.__instance is None:
            EventMaster(n_clients=n_clients)
        return EventMaster.__instance

    def __init__(self,n_clients):
        if EventMaster.__instance is not None:
            msg = "Trying to initalize multiple instances of EventMaster, this is forbidden to avoid side-effects.\n Call EventMaster.get_instance() instead."
            raise NotImplementedError(msg)
        else:

            # Initializing attributes
            self.n_clients = n_clients
            self.__n_clients_connected = 0
            self.__identified_clients = {}
            self.__open_sessions = set()

            # Standard python-socketio server
            self.sio = socketio.AsyncServer(async_mode="aiohttp", async_handlers=True, cors_allowed_origins="*")
            self.app = web.Application()

            # Starting asyncio stuff
            self.event_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.event_loop)

            # Attaching the app
            self.sio.attach(self.app)

            self.runner = web.AppRunner(self.app)

            # Shutdown callback
            async def on_shutdown(_):
                self.__n_clients_connected=0
                for x in self.__open_sessions:
                    await self.sio.disconnect(x)
                self.__open_sessions = set()

            self.app.on_shutdown.append(on_shutdown)

            @self.sio.event()
            def connect(sid,*_):
                """
                    Handling incoming connections
                """
                self.__open_sessions.add(sid)
                self.__n_clients_connected += 1
                #print(f"Waiting for listeners {self.__n_clients_connected} out of {self.n_clients} are connected.")

            @self.sio.on("play")
            async def handle_play(*_):
                #await self.sio.emit('play',data)
                return None

            @self.sio.on("identify")
            async def handle_identify(sid,data):
                #print("Identifying a listener")
                #print(json.loads(data).get("identifier",0))
                self.__identified_clients[json.loads(data).get("identifier",0)]=sid

            # Setting the singleton instance
            EventMaster.__instance = self

    async def wait_for_identified_client(self,name:str) -> str:
        """ Waits for an identified client (a player typically)

        Args:
            name (str): the name of the remote client
        Returns:
            str: the client sid
        """
        while not self.__identified_clients.get(name,None):
            await asyncio.sleep(1)
        return self.__identified_clients.get(name)

    async def _wait_for_connexion(self) -> None:
        """
            Coroutine that completes when the number of listening socketIO connexions
            is equal to `EventMaster.__instance.n_clients`
        """
        #print(f"Waiting for listeners {self.__n_clients_connected} out of {self.n_clients} are connected.")
        while not self.__n_clients_connected==self.n_clients:
            await asyncio.sleep(1)

    def start(self,task:Callable[[None],None],listeners:list[EventSlave]) -> None:
        """
            Starts an emitting sequence and runs a tasks that embeds
            calls to `EventMaster.__instance.sio.emit()`

            The emitting sequence waits for a number of socketIO connections
            specified in `EventMaster.__instance.n_clients`.

            If `EventMaster.__instance.n_clients==0` emits events
            in the void.

            Args:
                task (Callable[[None],None]): task calling `EventMaster.sio.emit()`
        """

        # Sets the runner up and starts the tcp server
        self.event_loop.run_until_complete(self.runner.setup())
        site = web.TCPSite(self.runner, "localhost", "8080")
        self.event_loop.run_until_complete(site.start())


        async def stop():
            for x in listeners:
                await x.listen(keep_alive=False)

            # Waiting for all listeners
            await self._wait_for_connexion()

            # Launching the task
            task_future = asyncio.wrap_future(self.sio.start_background_task(task))
            await task_future

            # Cleaning up and closing the runner upon completion
            try:
                await asyncio.wait_for(self.runner.cleanup(), timeout=1)
            except TimeoutError:
                pass

        # Blocking call to the procedure
        self.event_loop.run_until_complete(stop())
        self.event_loop.run_until_complete(site.stop())

