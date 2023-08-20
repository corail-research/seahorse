# Networking

Here you will find some insights on how the internals of Seahorse work and hopefully when you are done reading this you will understand how the networking features were brought to life.

## An master-slave mechanism
``` mermaid
graph TD
  M{Master};
  M <--> C[GUIClient];
  M <--> F[StateRecorder];
  M <--> D(Player #1);
  M <--> E(Player #2);
  M <--> G[SocketIO client];
```

## Proxies

## In-house handshake

``` mermaid
sequenceDiagram
  autonumber
  Client->>Server: Connexion request
  Server->>Client: Connexion accepted
  Client->>Server: Identifier : "Bob"
  loop wait for states
      Client->>Client: sleep
      Server->>Client: State (+ action request)
      Client-->>Server: (Action)
  end
  Server->>Client: Terminate connexion
```
