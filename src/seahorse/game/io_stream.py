from __future__ import annotations

import asyncio
import functools
import json
from collections import deque
from typing import TYPE_CHECKING, Any, Callable, List, Tuple, Type

import socketio
from aiohttp import web

from seahorse.game.action import Action
from seahorse.utils.serializer import Serializable

if TYPE_CHECKING:
    from seahorse.game.game_state import GameState


class EventSlave:

    def activate(self,
                 identifier:str=None,
                 wrapped_id:int=None,
                 *,
                 masterless:bool=False
                 ) -> None:
        self.sio = socketio.AsyncClient()
        self.connected = False
        self.identifier = identifier
        self.wrapped_id = wrapped_id

        @self.sio.event()
        async def connect():
            self.connected = True
            if self.identifier is not None:
                await self.sio.emit("identify", json.dumps(self.__dict__, default=lambda _: "bob"))

        @self.sio.event()
        def disconnect():
            self.connected = False


    async def listen(self,master_address,*,keep_alive:bool) -> None:
        if not self.connected:
            await self.sio.connect(master_address)
        if keep_alive:
            while self.connected:
                await asyncio.sleep(.1)

def event_emitting(label:str):
    def meta_wrapper(fun: Callable[[Any],Action]):
        @functools.wraps(fun)
        async def wrapper(self:EventSlave,*args,**kwargs):
            out = fun(self,*args, **kwargs)
            #print(label)
            #print(json.dumps(out.to_json(),default=lambda x:x.to_json()))
            await self.sio.emit(label,json.dumps(out.to_json(),default=lambda x:x.to_json()))
            #print("pooof")
            return out

        return wrapper

    return meta_wrapper


def remote_action(label: str):
    def meta_wrapper(fun: Callable):
        @functools.wraps(fun)
        async def wrapper(self:EventSlave,current_state:GameState,*_,**__):
            print("____________----------+++",current_state)
            await EventMaster.get_instance().sio.emit(label,json.dumps(current_state.to_json(),default=lambda x:x.to_json()),to=self.sid)
            print("xxxxx")
            out = await EventMaster.get_instance().wait_for_next_play(self.sid,current_state.players)
            #print("++++++")
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
    def get_instance(n_clients:int=1,game_state:type=Serializable,port: int = 8080,hostname: str="localhost") -> EventMaster:
        """Gets the instance object

        Args:
            n_clients (int, optional): the number of clients the instance is supposed to be listening, *ignored* if already initialized. Defaults to 1.
            game_state : class of a game state
            port (int, optional): the port to use. Defaults to 8080.

        Returns:
            object: _description_
        """
        if EventMaster.__instance is None:
            EventMaster(n_clients=n_clients,game_state=game_state, port=port, hostname=hostname)
        return EventMaster.__instance

    def __init__(self,n_clients,game_state,port,hostname):
        if EventMaster.__instance is not None:
            msg = "Trying to initialize multiple instances of EventMaster, this is forbidden to avoid side-effects.\n Call EventMaster.get_instance() instead."
            raise NotImplementedError(msg)
        else:
            # Initializing attributes
            self.n_clients = n_clients
            self.__n_clients_connected = 0
            self.__identified_clients = {}
            self.__open_sessions = set()
            self.__ident2sid = {}
            self.__sid2ident = {}
            self.__events = {}
            self.__game_state = game_state
            self.port = port
            self.hostname = hostname

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
                for x in list(self.__open_sessions):
                    if x in self.__open_sessions:
                        await self.sio.disconnect(x)

            self.app.on_shutdown.append(on_shutdown)

            @self.sio.event()
            def connect(sid, *_):
                """
                    Handling incoming connections
                """
                self.__open_sessions.add(sid)
                self.__n_clients_connected += 1
                print(f"Waiting for listeners {self.__n_clients_connected} out of {self.n_clients} are connected.")

            @self.sio.event
            def disconnect(sid):
                print("Lost connection: ", sid)
                self.__n_clients_connected -= 1
                self.__open_sessions.remove(sid)
                if sid in self.__sid2ident.keys() and self.__sid2ident[sid] in self.__identified_clients:
                    print(f"Client identified as {self.__sid2ident[sid]} was lost.")
                    del self.__identified_clients[self.__sid2ident[sid]]

            @self.sio.on("*")
            async def catch_all(event,_,data):
                self.__events[event] = self.__events.get(event,deque())
                self.__events[event].appendleft(data)

            @self.sio.on("action")
            async def handle_play(sid,data):
                # TODO : cope with race condition "action" before "identify"
                self.__identified_clients[self.__sid2ident[sid]]["incoming"].appendleft(data)

            @self.sio.on("identify")
            async def handle_identify(sid,data):
                print("Identifying a listener")
                print(json.loads(data).get("identifier",0))
                print(json.loads(data))
                data = json.loads(data)
                # TODO check presence of "id" in data
                self.__ident2sid[data.get("identifier",0)]=sid
                self.__sid2ident[sid]=data.get("identifier",0)
                self.__identified_clients[data.get("identifier",0)]={"sid":sid,"id":data["wrapped_id"],"incoming":deque()}



            # Setting the singleton instance
            EventMaster.__instance = self

    async def wait_for_next_play(self,sid,players:list) -> Action:
        # TODO revise sanity checks to avoid critical errors
        print("waiting for next play",print(sid))
        while not len(self.__identified_clients[self.__sid2ident[sid]]["incoming"]):
            print(self.__identified_clients[self.__sid2ident[sid]]["incoming"])
            await asyncio.sleep(.1)
        print("next play received")
        action = json.loads(self.__identified_clients[self.__sid2ident[sid]]["incoming"].pop())
        next_player_id = int(action["new_gs"]["next_player"]["id"])
        next_player = list(filter(lambda p:p.id==next_player_id,players))[0]

        past_gs = self.__game_state.from_json(json.dumps(action["past_gs"]))
        past_gs.players = players
        new_gs = self.__game_state.from_json(json.dumps(action["new_gs"]),next_player=next_player)
        new_gs.players = players


        return Action(past_gs,new_gs)

    async def wait_for_event(self,label):
        while not len(self.__events.get(label,[])):
            await asyncio.sleep(1)
        data = self.__events[label].pop()
        return data

    async def wait_for_identified_client(self,name:str,local_id:int) -> str:
        """ Waits for an identified client (a player typically)

        Args:
            name (str): the name of the remote client
        Returns:
            str: the client sid
        """
        while not self.__identified_clients.get(name, None):
            await asyncio.sleep(.1)

        cl = self.__identified_clients.get(name)

        # Check sid
        await self.sio.emit("update_id",json.dumps({"new_id":local_id}),to=cl["sid"])

        return cl

    async def _wait_for_connexion(self) -> None:
        """
            Coroutine that completes when the number of listening socketIO connexions
            is equal to `EventMaster.__instance.n_clients`
        """
        # print(f"Waiting for listeners {self.__n_clients_connected} out of {self.n_clients} are connected.")
        while not self.__n_clients_connected == self.n_clients:
            await asyncio.sleep(.1)

    def start(self, task: Callable[[None], None], listeners: list[EventSlave]) -> None:
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
        #print(self.port)
        site = web.TCPSite(self.runner, self.hostname, self.port)
        self.event_loop.run_until_complete(site.start())

        async def stop():
            for x in listeners:
                await x.listen(master_address=f"http://{self.hostname}:{str(self.port)}", keep_alive=False)

            # Waiting for all listeners
            await self._wait_for_connexion()
            print("started")

            # Launching the task
            task_future = asyncio.wrap_future(self.sio.start_background_task(task))
            await task_future

            # Cleaning up and closing the runner upon completion
            try:
                await asyncio.wait_for(self.runner.cleanup(), timeout=1)
            except asyncio.exceptions.TimeoutError:
                pass

        # Blocking call to the procedure
        self.event_loop.run_until_complete(stop())
