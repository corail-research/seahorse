# Time limits and Fairness

Seahorse enforces a **time budget per player**.
The budget is set when you create the game master (e.g., 60 seconds for the entire match).
This section explains how time is tracked, enforced, and what happens when a player exceeds their budget.

## How time limits work

Each player starts with the same total time budget. During each turn, the game master:

1. Calls [`play`][seahorse.player.proxies.PlayerProxy.play] method from proxies.
2. Measures the time taken - including network latency for remote proxies.
3. Subtracts the elapsed time returned by the proxy from the player’s remaining budget.
4. If the remaining budget becomes negative, the player is disqualified immediately.

The master uses [`asyncio.wait_for`][] to impose a **hard deadline** for each move.
Do note this deadline don't work if the proxy run on the same process as the master due to Python limitations and compatibility issues with most OS.

## Enforcement per proxy type

| Proxy type | How timeout is enforced |
|------------|-------------------------|
| **ContaineredPlayerProxy** | Agent runs in a separate OS process. If timeout occurs, the process is **terminated** and the player disqualified. |
| **RemotePlayerProxy** | Master waits for a WebSocket `"action"` response. If the remote agent does not reply within the remaining time, the connection is closed and the player disqualified. |
| **LocalPlayerProxy** | Time is measured but **not enforced**. If the agent blocks, the whole game freezes. Only use this proxy on a remote machine or for debbugging. |
| **InteractivePlayerProxy** | No time limit (human players think at their own pace). |

## Disqualification

When a player is disqualified (timeout or illegal action), the game master:

- Assigns a very low score (`-1e9`) to the disqualified player.
- Assigns a very high score (`1e9`) to all remaining players.
- Ends the game immediately. Disqualified players are excluded from the list of winners.

!!! info

    Default behavior can be overriden by subclassing [GameMaster][seahorse.game.master.GameMaster] and designing your [GameState][seahorse.game.game_state.GameState] accordingly.

??? example "Initialize GameMaster with custom time limit"

    ```python
    master = GameMaster(
        name="Fast Game",
        initial_game_state=start_state,
        players_iterator=[proxy1, proxy2],
        time_limit=30.0   # 30 seconds per player for the whole match
    )
    ```

---

## See also

- [Architecture](architecture.md) – for the role of timeouts in the game loop.
- [Game Design](game-design.md) – for implementing winner logic after disqualification.
- [Agent and Proxies](agents-proxies.md) – for which proxy types enforce time limits.
- [Networking and Communication](networking-communication.md) – for timeouts with remote agents.
- [API Reference – GameMaster][seahorse.game.master.GameMaster]
