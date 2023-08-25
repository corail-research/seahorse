https://squidfunk.github.io/mkdocs-material/reference/diagrams/
``` mermaid
classDiagram

  GameState *--  Action
  Action *--"2"  GameState
  GameMaster *-- GameState
  GameState *--"1" Representation
  Representation <|-- Board
  Board *-- Piece
  GameMaster *-- Player
  GameState *-- Player
  
  class GameState{
    +Representation rep
    +dict[int, Any] scores
    +Player next_player
    +list[Player] players
    +list[Action] _possible_actions
    +GameState(scores, next_player, players, rep)  
    +get_player_score(player) float
    +compute_next_player() Player
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
    +compute_winner(scores)* list[Player] 
  }

  class Representation{
    +Dict env
    +Representation(env)
    +find(to_find) Any
  }

  class Board{
    +list[int] dimensions
    +get_pieces_player(owner) tuple[int, list[Piece]]
  }

  class Piece{
    +str piece_type
    +int owner_id
  }

  class Player{
    +int id
    +str name
    +Player(name, id, time_limit)
    +play(game_state) Action
    +compute_action(...)* Action
  }
```
