from __future__ import annotations

import asyncio
import functools
import json
import time
import re
import socketio

from typing import TYPE_CHECKING, Any, Callable, Coroutine
from aiohttp import web
from loguru import logger
from collections import deque

from seahorse.game.action import Action
from seahorse.game.heavy_action import HeavyAction
from seahorse.utils.serializer import Serializable

if TYPE_CHECKING:
    from seahorse.game.game_state import GameState


class EventSlave:

    def activate(self,
                 identifier:str | None = None,
                 wrapped_id:int | None = None,
                 *,
                 disconnected_cb: Callable[[None],None] | None = None
                 ) -> None:
        """
        Sets the listener up, binds handlers

        Args:
            identifier (str | None, optional): Must be a unique identifier. Defaults to None.
            wrapped_id (int | None, optional): If the eventSlave is bound to an instance a python native id might be associated. 
                                               Defaults to None.
        """
        self.sio = socketio.AsyncClient()
        self.connected = False
        self.identifier = identifier
        self.wrapped_id = wrapped_id
        self.disconnected_cb = disconnected_cb

        @self.sio.event()
        async def connect():
            self.connected = True
            if self.identifier is not None:
                await self.sio.emit("identify", json.dumps(self.__dict__,default=lambda _:"_"))

        @self.sio.event
        def disconnect():
            self.connected = False


    async def listen(self,master_address:str,*,keep_alive:bool) -> None:
        """Fires up the listening process

        Args:
            master_address (str): the address to listen to
            keep_alive (bool): in standalone mode, this should be `True` to keep the asyncio process alive.
        """
        if not self.connected:
            await self.sio.connect(master_address)
        if keep_alive:
            while self.connected:
                await asyncio.sleep(.1)

def event_emitting(label:str):
    """Decorator to also send the function's output trough listening socket connexions

    Args:
        label (str): the type of event to emit
    """
    def meta_wrapper(fun: Callable[[Any],Action]):
        @functools.wraps(fun)
        async def wrapper(self:EventSlave,*args,**kwargs):
            out = fun(self,*args, **kwargs)
            await self.sio.emit(label,json.dumps(out.to_json(),default=lambda x:x.to_json()))
            return out

        return wrapper

    return meta_wrapper


def remote_action(label: str):
    """Proxy decorator to override an expected local behavior with a distant one
       *The logic in decorated function is ignored*
    Args:
        label (str): the time of event to emit to trigger the distant logic
    """
    def meta_wrapper(fun: Callable):
        @functools.wraps(fun)
        async def wrapper(self:EventSlave,current_state:GameState,*_,**kwargs):
            await EventMaster.get_instance().sio.emit(label,json.dumps({**current_state.to_json(),**kwargs},
                                                                       default=lambda x:x.to_json()),
                                                                       to=self.sid)
            out = await EventMaster.get_instance().wait_for_next_play(self.sid,current_state.players)
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
    def get_instance(game_state:type=Serializable,port: int = 8080,hostname: str="localhost") -> EventMaster:
        """Gets the instance object

        Args:
            n_clients (int, optional): the number of clients the instance is supposed to be listening, 
                                       *ignored* if already initialized. Defaults to 1.
            game_state : class of a game state
            port (int, optional): the port to use. Defaults to 8080.

        Returns:
            object: _description_
        """
        if EventMaster.__instance is None:
            EventMaster(game_state=game_state, port=port, hostname=hostname)
        return EventMaster.__instance

    def __init__(self,game_state,port,hostname):
        if EventMaster.__instance is not None:
            msg = "Trying to initialize multiple instances of EventMaster, this is forbidden to avoid side-effects.\n Call EventMaster.get_instance() instead."
            raise NotImplementedError(msg)
        else:
            # Initializing attributes
            self.expected_clients = 0
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
            self.sio = socketio.AsyncServer(async_mode="aiohttp", async_handlers=True, 
                                            cors_allowed_origins="*", ping_timeout=1e6)
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
                logger.info(f"Waiting for listeners {self.__n_clients_connected} out of {self.expected_clients} are connected.")

            @self.sio.event
            def disconnect(sid):
                logger.warning(f"Lost connection: {sid}")
                self.__n_clients_connected -= 1
                self.__open_sessions.remove(sid)
                if sid in self.__sid2ident.keys() and self.__sid2ident[sid] in self.__identified_clients:
                    logger.warning(f"Client identified as {self.__sid2ident[sid]} was lost.")
                    del self.__identified_clients[self.__sid2ident[sid]]

            @self.sio.on("*")
            async def catch_all(event,sid,data):
                self.__events[sid] = self.__events.get(sid,{})
                self.__events[sid][event] = self.__events[sid].get(event,deque())
                self.__events[sid][event].appendleft((time.time(),data))

            @self.sio.on("action")
            async def handle_play(sid,data):
                # TODO : cope with race condition "action" before "identify"
                try:
                    self.__identified_clients[self.__sid2ident[sid]]["incoming"].appendleft(data)
                # Plainly throw away packets that belong to disconnected clients
                except KeyError:
                    pass

            @self.sio.on("identify")
            async def handle_identify(sid,data):
                logger.info("Identifying a listener")
                logger.info(json.loads(data).get("identifier",0))
                logger.debug(f"Deserialized data {json.loads(data)}")
                data = json.loads(data)

                # TODO check presence of "id" in data
                idf = data.get("identifier",0)
                reg = r"^"+idf+r"(_duplicate_[0-9]+$|$)"
                if len(list(filter(lambda x:re.search(reg,x),self.__ident2sid.keys()))):
                    logger.warning("Two clients are using the same identifier, one of those will be ignored.")
                    idf = idf+"_duplicate_"+str(time.time())

                self.__ident2sid[idf]=sid
                self.__sid2ident[sid]=idf
                self.__identified_clients[idf]={"sid":sid,"id":data.get("wrapped_id",None),"incoming":deque(),"attached":False}


            # Setting the singleton instance
            EventMaster.__instance = self

    async def wait_for_next_play(self,sid:int,players:list) -> Action:
        """Waiting for the next play action, this function is blocking

        Args:
            sid (int): sid corresponding to the player to wait for
            players (list): the list of players

        Returns:
            Action: returns the received action
        """
        # TODO revise sanity checks to avoid critical errors
        logger.info(f"Waiting for next play from {self.__sid2ident[sid]}")
        while not len(self.__identified_clients[self.__sid2ident[sid]]["incoming"]):
            await asyncio.sleep(.1)
        logger.info("Action received")
        action = json.loads(self.__identified_clients[self.__sid2ident[sid]]["incoming"].pop())
        next_player_id = int(action["next_game_state"]["next_player"]["id"])
        next_player = next(iter(list(filter(lambda p:p.id==next_player_id,players))))

        past_gs = self.__game_state.from_json(json.dumps(action["current_game_state"]))
        past_gs.players = players
        new_gs = self.__game_state.from_json(json.dumps(action["next_game_state"]),next_player=next_player)
        new_gs.players = players


        return HeavyAction(past_gs,new_gs)

    async def wait_for_event(self,sid:int,label:str,*,flush_until:float | None=None) -> Coroutine:
        """Waits for an aribtrary event emitted by the connection identified by `sid`
           and labeled with `label`.
           One might want to ignore all events before a particular timestamp given in `flush_until`

        Args:
            sid (int): a socketio connexion identifier
            label (str): the event to wait for
            flush_until (float, optional): The timestamp treshold. Defaults to None.

        Returns:
            Coroutine: a promise yielding the data associated to the event
        """
        while not len(self.__events.get(sid,{}).get(label,[])):
            await asyncio.sleep(.1)
        ts,data = self.__events[sid][label].pop()

        if (not flush_until) or ts>=flush_until:
            return data
        else :
            await self.wait_for_event(sid,label,flush_until=flush_until)

    async def wait_for_identified_client(self,name:str,local_id:int) -> str:
        """ Waits for an identified client (a player typically)

        Args:
            name (str): the name of the remote client
        Returns:
            str: the client sid
        """
        reg = r"^"+name+r"([0-9]+$|$)"
        def unattached_match(x):
            return re.search(reg, x) and not self.__identified_clients.get(x)["attached"]
        matching_names = list(filter(unattached_match,self.__ident2sid.keys()))
        while not len(matching_names):
            await asyncio.sleep(.1)
            matching_names = list(filter(unattached_match,self.__ident2sid.keys()))

        cl = self.__identified_clients.get(matching_names[0])
        self.__identified_clients[matching_names[0]]["attached"] = True

        await self.sio.emit("update_id",json.dumps({"new_id":local_id}),to=cl["sid"])
        return cl

    def start(self, task: Callable[[None], None], listeners: list[EventSlave]) -> None:
        """
            This method is blocking.

            Starts an emitting sequence and runs a tasks that embeds
            calls to `EventMaster.__instance.sio.emit()`

            The game is starting when for all `EventSlave` in `listeners`, the `.listen()` future is fulfilled.

            If `len(listeners)==0` the EventMaster emits events in the void.

            Args:
                task (Callable[[None],None]): task calling `EventMaster.sio.emit()`
        """
        slaves = list(filter(lambda x:isinstance(x,EventSlave),listeners))
        self.expected_clients = len(slaves)

        # Sets the runner up and starts the tcp server
        self.event_loop.run_until_complete(self.runner.setup())
        site = web.TCPSite(self.runner, self.hostname, self.port)
        self.event_loop.run_until_complete(site.start())

        async def stop(task):
            # Waiting for all listeners to connect
            logger.info(f"Waiting for listeners {self.__n_clients_connected} "
                        f"out of {self.expected_clients} are connected.")
            for x in slaves:
                await x.listen(master_address=f"http://{self.hostname}:{self.port!s}", keep_alive=False)

            # Launching the task
            logger.info("Starting match")
            task_future = self.sio.start_background_task(task)

            # Await the game task completion
            try:
                await task_future
            except asyncio.CancelledError:
                logger.warning("Game task was cancelled.")


            # Explicitly cancel any remaining tasks related to disconnected clients
            # logger.info("Canceling pending tasks related to disconnected clients.")
            tasks = [task for task in asyncio.all_tasks() if task is not asyncio.current_task()]
            for task in tasks:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass

        # Blocking call to the procedure
        self.event_loop.run_until_complete(stop(task))
