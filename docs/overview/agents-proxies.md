# Agents and Proxies

This page covers two related topics: how to **design an agent** (the AI logic) and how Seahorse **runs that agent** using different proxies.

---

## Agent Design

An **agent** is the decision‑making component that chooses actions given a game state.

### For players - implementing your own agent

To create a playable agent for an existing game, you at least need to subclass [`Player`][seahorse.player.player.Player] and implement its [`compute_action`][seahorse.player.player.Player.compute_action] method.
This method is called by the game master when your agent needs to play, the current [game state][seahorse.game.game_state.GameState] is defined as the first argument of that method.
Other keyword arguments can also be set to give more context and information to the player.
Such arguments should be clearly defined and communicated by the game designers.

??? example "Agent example with random action choice"

    ```python
    from seahorse.player.player import Player
    from seahorse.game.action import Action

    import random

    class MyRandomAgent(Player):
        def compute_action(self, current_state, **kwargs):
            # Faster with stateless actions
            actions = list(current_state.get_possible_stateless_actions())
            # But also possible with stateful actions
            # actions = list(current_state.get_possible_stateful_actions())
            return random.choice(actions)
    ```

When designing your agent, take in considerations your game designer directives and the following:

- Make sure to use the subclass of the `game` module that your game designers created.
  For example, `current_state` in [`compute_action`][seahorse.player.player.Player.compute_action] will likely be a subclass of the original [game state][seahorse.game.game_state.GameState].
  If you want to create your own versions of [game state][seahorse.game.game_state.GameState] or [action][seahorse.game.action.Action], you'll need to take their implementation as a starting point and transform them in your [`Player`][seahorse.player.player.Player] subclass.
- The `kwargs` arguments may include a `remaining_time` key (the time left for this player).
  You can use it to decide how deep to search.
- The returned action must be one of the legal actions.
  If it is not, the game master will disqualify your agent.
  Relly on `get_possible_*_actions` methods to ensure you return a correct action.

### For game designers - providing an agent template for players

If you are designing a game, you may want to provide a **baseline agent** or a **template** that players can extend.
For example, a random agent or a subclass with already made game-specific method.
We suggest some good practices:

- Provide an abstract *`MyGamePlayer`* subclass or template of [`Player`][seahorse.player.player.Player] that implements common utilities (e.g., board evaluation, move generation), an abstract or incomplete `compute_action` method with more accurate arguments list and your own JSON serialization/deserialization methods if needed.
- Include a fully functional example agent (e.g., random or minimax) so players have a working starting point.
- Indicate clear directives for your players about the expected implementations and specific limitation of your game design.

??? example "Player subclass suggestion for Tic-Tac-Toe"

    ```python
    from abc import abstractmethod

    from seahorse.player.player import Player
    from seahorse.game.action import StatelessAction

    class TicTacToePlayer(Player):
        """Base class for Tic‑Tac‑Toe agents."""

        def get_empty_cells(self, state):
            rep = state.get_rep().get_env()
            return [(r,c) for r in range(3) for c in range(3) if rep["board"][r][c] == 0]

        @abstractmethod
        def compute_action(self, current_state, remaining_time, **kwargs):
            pass
    ```

    Players then inherit from your template and only override `compute_action`.

---
## Proxy Types

A **[proxy][seahorse.player.proxies.PlayerProxy]** is a wrapper that allows the game master to interact with an agent regardless of where it runs.
All proxies implement the same asynchronous [`play`][seahorse.player.proxies.PlayerProxy.play] method, so the game master never needs to know which one it is using.
This behavior helps both player and game designers by ensuring they can focus only on the game logic and make it run almost anywhere.
Proxies should be transmitted to the [`GameMaster`][seahorse.game.master.GameMaster] on initialization.

### Detailed descriptions of each proxy

#### [ContaineredPlayerProxy][seahorse.player.proxies.ContaineredPlayerProxy] - for local agent
Uses a [`PlayerContainer`][seahorse.player.contrainers.PlayerContainer] (based on [`aioprocessing`](https://github.com/dano/aioprocessing)).
The agent runs in a separate process.
Communication goes through multiprocessing queues.
The master waits for the action using [asyncio.wait_for][]. If the timeout expires, the entire subprocess is terminated.

#### [LocalPlayerProxy][seahorse.player.proxies.LocalPlayerProxy] - to run agent on a distant machine
Wraps a local [`Player`][seahorse.player.player.Player] instance.
Inherits from [`EventSlave`][seahorse.game.io_stream.EventSlave] and listens for `"turn"` events that indicate the distant game master wait for their action.
When a turn arrives, it calls [`compute_action`][seahorse.player.player.Player.compute_action] directly, and emits an `"action"` event with the action and elapsed time data.
Work with [`RemotePlayerProxy`][seahorse.player.proxies.RemotePlayerProxy] in a distributed setup.

#### [RemotePlayerProxy][seahorse.player.proxies.RemotePlayerProxy] - endpoint for distant agent
Does not hold a real agent and only use a `mimic`.
The `mimic` provides the player’s name and ID for serialisation and identification, but the actual action computation happens remotely.
On `play()`, it emits a `"turn"` event over WebSocket and waits for an `"action"` response from the distant agent.
The remote client must run a [`LocalPlayerProxy`][seahorse.player.proxies.LocalPlayerProxy] (or any [`EventSlave`][seahorse.game.io_stream.EventSlave] that replies to `"turn"` with `"action"`).

#### [InteractivePlayerProxy][seahorse.player.proxies.InteractivePlayerProxy] - process human player actions
Inherits from [`LocalPlayerProxy`][seahorse.player.proxies.LocalPlayerProxy] but overrides `play` to wait for a human input, for example through a GUI.
It validates the input against legal actions and ask for another action if invalid.

!!! warning

    This description can be the subject of changes throughout new Seahorse versions.
    By either adding new proxies or enabling new functionalities for existing proxies.

## How to choose a proxy

The table below helps you decide which proxy to use based on your needs.

| If you want... | Use this proxy |
|----------------|----------------|
| A local player with process isolation and timeout | [`ContaineredPlayerProxy`][seahorse.player.proxies.ContaineredPlayerProxy] |
| A remote agent on another machine | [`RemotePlayerProxy`][seahorse.player.proxies.RemotePlayerProxy] (master) + [`LocalPlayerProxy`][seahorse.player.proxies.LocalPlayerProxy] (client) |
| A human player via a graphical interface | [`InteractivePlayerProxy`][seahorse.player.proxies.InteractivePlayerProxy] |
| A simple local agent (for debugging) | [`LocalPlayerProxy`][seahorse.player.proxies.LocalPlayerProxy] (master side) |

---
## See also

- [Architecture](architecture.md) – for the role of proxies in the event hub.
- [Game Design](game-design.md) – for creating the game state and actions.
- [Networking and Communication](networking-communication.md) – for how remote proxies serialise data.
- [Time Limits and Fairness](time-fairness.md) – for timeout enforcement per proxy type.
- [API Reference – Player][seahorse.player.player.Player]
- [API Reference – Proxies][seahorse.player.proxies.PlayerProxy]

