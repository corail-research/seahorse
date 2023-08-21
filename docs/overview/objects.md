https://squidfunk.github.io/mkdocs-material/reference/diagrams/
``` mermaid
classDiagram

  GameState *--  Action
  Action *--  GameState
  GameMaster *-- GameState
  GameState *-- Representation
  
  class GameState{
    +Representation rep
    +dict[int, Any] scores
    +Player next_player
    +list[Player] players
    +list[Action] _possible_actions
    +GameState(scores, next_player, players, rep)  
    +get_player_score(player) float
    +get_next_player() Player
    +compute_next_player() Player
    +get_scores() dict[int, Any]
    +get_players() list[Player]
    +get_rep() Representation
    +get_possible_actions() frozenset[Action]
    +check_action(action) bool
    +generate_possible_actions()* Set[Action]
    +compute_scores(next_rep)* dict[int, Any]
    +is_done()* bool
  }

  class Action{
    +GameState past_gs 
    +GameState next_gs
    +Action(past_gs, next_gs)
    +get_current_game_state() GameState
    +get_next_game_state() GameState
  }

  class GameMaster{
    +EventMaster emitter
    +GameState current_game_state
    +String name
    +GameState initial_game_state
    +list[Player] players
    +String log_level
    +GameMaster(name,initial_game_state,players_iterator,log_level,port,hostname)
    +step()
    +play_game() list[Player]
    +record_game(listeners)
    +update_log()
    +get_name() String
    +get_game_state() GameState
    +get_winner() Player
    +get_scores() dict[int, Any]
    +compute_winner(scores)* list[Player] 
  }

  class Representation{
    +Dict env
    +Representation(env)
    +get_env() Dict
    +find(to_find) Any
  }
```
