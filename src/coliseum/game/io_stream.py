import asyncio
import socketio
from aiohttp import web
from typing import Callable, List



class EventSlave:

    def __init__(self) -> None:
        self.sio = socketio.AsyncClient() 
        @self.sio.event()
        def connect():
            print("boom")
    
    async def listen(self) -> None:
        await self.sio.connect('http://localhost:5000')

class EventMaster:
    """
    Singleton for emitting events

    Attributes:


    Raises:
        NotImplementedError: when trying to initialize more than once

    """

    __instance = None

    @staticmethod
    def get_instance(n_clients:int=1) -> object:
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
            raise NotImplementedError("Trying to initalize multiple instances of EventMaster, this is forbidden to avoide side-effects.")
        else:

            # Initializing attributes
            self.n_clients = n_clients
            self.__clients_connected = 0

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
                self.__clients_connected=0

            self.app.on_shutdown.append(on_shutdown)

            @self.sio.event
            def connect(*_):
                """
                    Handling incoming connections
                """
                self.__clients_connected += 1
                print(f"Waiting for listeners {self.__clients_connected} out of {self.n_clients} are connected.")

            # Setting the singleton instance
            EventMaster.__instance = self

    async def _wait_for_connexion(self) -> None:
        """ 
            Coroutine that completes when the number of listening socketIO connexions
            is equal to `EventMaster.__instance.n_clients`
        """
        print(f"Waiting for listeners {self.__clients_connected} out of {self.n_clients} are connected.")
        while not self.__clients_connected==self.n_clients:
            await asyncio.sleep(1)

    def start(self,task:Callable[[None],None],listeners:List[EventSlave]) -> None:
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
        site = web.TCPSite(self.runner, 'localhost', '5000')
        self.event_loop.run_until_complete(site.start())


        async def stop():
            for x in listeners:
                await x.listen()

            # Waiting for all listeners
            await self._wait_for_connexion()

            # Launching the task
            task_future = asyncio.wrap_future(self.sio.start_background_task(task))
            await task_future

            # Cleaning up and closing the runner upon completion
            try:
                await asyncio.wait_for(self.runner.cleanup(), timeout=.1)
            except TimeoutError:
                pass

        # Blocking call to the procedure
        self.event_loop.run_until_complete(stop())

