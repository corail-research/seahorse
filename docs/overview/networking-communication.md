# Networking and Communication

This page focuses on the **data serialisation** and **listener protocol** used by Seahorse.
For the overall architecture, see the [Architecture](architecture.md) page.

---

## JSON serialisation

All game states, players and actions must be converted to JSON-like structure before being sent over the network.
Seahorse provides a [`Serializable`][seahorse.utils.serializer.Serializable] base class that every core object inherits from.

When you create a custom game state or action, you must implement two methods:

- [`to_json`][seahorse.utils.serializer.Serializable.to_json] – returns a JSON‑serialisable dictionary (or string) representing the object.
- [`from_json`][seahorse.utils.serializer.Serializable.from_json] – a class method that reconstructs the object from JSON data.

The event hub automatically calls these methods when broadcasting and receiving data.
This allows a generic method for data transmition applied for any game implementation as long as they can parse JSON and understand the expected structure.

!!! example

    A `StatelessAction` stores a simple `data` dictionary.
    Its `to_json()` returns that dictionary; `from_json` creates a new instance with it.

---

## Listeners (spectators, recorders)

Any [`EventSlave`][seahorse.game.io_stream.EventSlave] can connect to the event hub without being a player. These **listeners** receive all broadcast events but never send actions. Common use cases:

- **[StateRecorder][seahorse.utils.recorders.StateRecorder]** – logs every `"play"` (game state) and `"done"` (final results) to a file for later replay or analysis.
- **Spectator GUI** – displays the game live.
- **Analytics tool** – collects statistics on the fly.

!!! tip

    At the time this documentation is written, only [StateRecorder][seahorse.utils.recorders.StateRecorder] is available and implemented through Seahorse package.
    Other types of listeners are just a suggestion that you can create for your game.
    Any contribution regarding other listeners implementation in Seahorse are welcomed.

### Implementing a custom listener

To create a listener, subclass [`EventSlave`][seahorse.game.io_stream.EventSlave] and override the event handlers you care about.
Event handlers hooks are leveraged through [SocketIO clients](https://python-socketio.readthedocs.io/en/latest/api_client.html#clients) and their [`on`](https://python-socketio.readthedocs.io/en/latest/api_client.html#socketio.Client.on) method.

??? example "Custom file save recorder"

    Create subclass `MyRecorder`

    ```python
    from seahorse.game.io_stream import EventSlave

    class MyRecorder(EventSlave):

        @self.sio.on("play")
        async def on_play(self, data):
            # data contains the serialised game state
            save_to_file(data)

        @self.sio.on("done")
        async def on_done(self, data):
            save_final_results(data)
    ```

    Then, register your listener when starting the game:

    ```python
    recorder = MyRecorder()

    # Activate and register the recorder when master start the game 
    master.record_game(listeners=[recorder])
    ```

    The listener will automatically receive all `"play"` and `"done"` events.

## Event names and payload structure

The event hub uses the following standard event names:

| Event | Direction | Target | Payload | Description |
|-------|-----------|--------|---------|-------------|
| `identify` | Client → Hub | Hub only | `{"identifier": str}` | Sent by a proxy to identify itself. |
| `update_id` | Hub → Client | Specific client | `{"new_id": int}` | Sent by the master to synchronise a player's ID. |
| `play` | Master → Hub → Clients | Active player (specific) + all listeners (broadcast) | Serialised game state | Broadcast when a new state is available. |
| `action` | Client → Hub → Master | Hub and Master only (specific) | Serialized action and elapsed time | Returned by a proxy after computing a move. |
| `done` | Master → Hub → Clients | Broadcast to all | Endgame informations | Sent when the game ends. |
| `interact` | Interface → Hub → InteractivePlayerProxy | Specific interactive proxy | Humain interface input data | Used only for human players. |

All payloads are JSON strings or tuples of JSON‑compatible data. The hub does not interpret the content – it only routes messages based on session IDs and event names.

---

## See also

- [Architecture](architecture.md) – for connection setup, identification, and message flow.
- [Agent and Proxies](agents-proxies.md) – for how proxies use `EventSlave`.
- [Time Limits and Fairness](time-fairness.md) – for network‑related timeouts.
- [API Reference – EventMaster][seahorse.game.io_stream.EventMaster]
- [API Reference – EventSlave][seahorse.game.io_stream.EventSlave]
