# Multiplayer & Networking

## Table of Contents
1. [Architecture Overview](#architecture-overview)
2. [High-Level Multiplayer API](#high-level-multiplayer-api)
3. [RPCs](#rpcs)
4. [MultiplayerSpawner & MultiplayerSynchronizer](#multiplayerspawner--multiplayersynchronizer)
5. [Authority & Ownership](#authority--ownership)
6. [Common Patterns](#common-patterns)
7. [Debugging Multiplayer](#debugging-multiplayer)

---

## Architecture Overview

Godot 4 uses a **peer-to-peer with authoritative server** model by default. One peer acts as the server (peer ID 1), others are clients.

### Network Topology
```
Server (peer_id = 1)
├── Client A (peer_id = 2)
├── Client B (peer_id = 3)
└── Client C (peer_id = 4)
```

### Setting Up Connection
```gdscript
# server.gd
func host_game(port: int = 9999) -> void:
    var peer := ENetMultiplayerPeer.new()
    var error := peer.create_server(port)
    if error != OK:
        push_error("Failed to create server: %s" % error)
        return
    multiplayer.multiplayer_peer = peer
    print("Server started on port %d" % port)

# client.gd
func join_game(address: String = "127.0.0.1", port: int = 9999) -> void:
    var peer := ENetMultiplayerPeer.new()
    var error := peer.create_client(address, port)
    if error != OK:
        push_error("Failed to connect: %s" % error)
        return
    multiplayer.multiplayer_peer = peer
```

### Connection Signals
```gdscript
func _ready() -> void:
    multiplayer.peer_connected.connect(_on_peer_connected)
    multiplayer.peer_disconnected.connect(_on_peer_disconnected)
    multiplayer.connected_to_server.connect(_on_connected_to_server)
    multiplayer.connection_failed.connect(_on_connection_failed)
    multiplayer.server_disconnected.connect(_on_server_disconnected)

func _on_peer_connected(id: int) -> void:
    print("Peer connected: %d" % id)

func _on_peer_disconnected(id: int) -> void:
    print("Peer disconnected: %d" % id)
    # Clean up player node
    var player_node := get_node_or_null(str(id))
    if player_node:
        player_node.queue_free()
```

---

## High-Level Multiplayer API

### Checking Peer Identity
```gdscript
# Am I the server?
multiplayer.is_server()

# My peer ID (1 = server)
multiplayer.get_unique_id()

# Check if multiplayer is active
multiplayer.has_multiplayer_peer()
```

---

## RPCs

RPCs (Remote Procedure Calls) let you call functions on other peers.

### RPC Annotations
```gdscript
# Called on all peers (including caller)
@rpc("any_peer", "call_local", "reliable")
func chat_message(msg: String) -> void:
    display_message(msg)

# Called only on the server
@rpc("any_peer", "reliable")
func request_spawn(spawn_pos: Vector2) -> void:
    if not multiplayer.is_server():
        return
    spawn_player(multiplayer.get_remote_sender_id(), spawn_pos)

# Called on specific peer
@rpc("authority", "reliable")
func update_health(new_health: int) -> void:
    health = new_health
    health_bar.value = new_health
```

### RPC Modes
```gdscript
@rpc("authority")    # Only the authority (server by default) can call this
@rpc("any_peer")     # Any peer can call this

# Call targets
@rpc("call_local")   # Also executes locally
@rpc("call_remote")  # Only on remote peers (default)

# Transfer modes
@rpc("reliable")     # TCP-like, guaranteed delivery
@rpc("unreliable")   # UDP-like, may be lost (use for position updates)
@rpc("unreliable_ordered")  # UDP but ordered

# Combined
@rpc("any_peer", "call_local", "reliable")
```

### Calling RPCs
```gdscript
# Call on all peers
chat_message.rpc("Hello everyone!")

# Call on specific peer
update_health.rpc_id(target_peer_id, 50)

# Call on server only
request_spawn.rpc_id(1, spawn_position)
```

---

## MultiplayerSpawner & MultiplayerSynchronizer

### MultiplayerSpawner
Automatically replicates node spawning across peers.

```
# Scene tree setup:
Game
├── MultiplayerSpawner (spawnable scenes configured in inspector)
└── Players (spawn path)
```

```gdscript
# Server spawns a player — automatically replicated to all clients
func spawn_player(peer_id: int) -> void:
    var player := player_scene.instantiate()
    player.name = str(peer_id)
    $Players.add_child(player)  # MultiplayerSpawner handles replication
```

### MultiplayerSynchronizer
Automatically syncs properties across peers.

```
# Add as child of the node to sync:
Player
├── MultiplayerSynchronizer
│   └── Synced properties: position, rotation, animation_state
├── Sprite2D
└── CollisionShape2D
```

```gdscript
# Configure in code:
var sync := MultiplayerSynchronizer.new()
sync.replication_config = SceneReplicationConfig.new()
# Add properties to sync
sync.replication_config.add_property(^".:position")
sync.replication_config.add_property(^".:rotation")
add_child(sync)
```

### Sync Intervals
```gdscript
# In the MultiplayerSynchronizer:
sync.replication_interval = 0.05  # 20 updates/sec (good for most games)
# Lower = smoother but more bandwidth
# Higher = less bandwidth but choppier
```

---

## Authority & Ownership

### Setting Authority
```gdscript
# By default, server (peer 1) has authority over everything
# Transfer authority to a specific peer:
player_node.set_multiplayer_authority(peer_id)

# Check who has authority
var auth_id: int = player_node.get_multiplayer_authority()

# Am I the authority for this node?
if player_node.is_multiplayer_authority():
    # Only I should process input for this player
    pass
```

### Authority-Based Input
```gdscript
func _physics_process(delta: float) -> void:
    # Only process input if we're the authority
    if not is_multiplayer_authority():
        return

    var input := Input.get_vector("move_left", "move_right", "move_up", "move_down")
    velocity = input * speed
    move_and_slide()
```

---

## Common Patterns

### Lobby System
```gdscript
# lobby.gd
var players: Dictionary[int, String] = {}  # peer_id -> player_name

@rpc("any_peer", "reliable")
func register_player(player_name: String) -> void:
    var sender_id: int = multiplayer.get_remote_sender_id()
    players[sender_id] = player_name
    # Broadcast updated player list to all
    update_player_list.rpc(players)

@rpc("authority", "call_local", "reliable")
func update_player_list(player_dict: Dictionary) -> void:
    players = player_dict
    # Update UI
    refresh_lobby_display()

@rpc("authority", "call_local", "reliable")
func start_game() -> void:
    get_tree().change_scene_to_file("res://scenes/game.tscn")
```

### Client-Side Prediction
```gdscript
# player.gd
var _server_position: Vector2
var _predicted_position: Vector2

func _physics_process(delta: float) -> void:
    if is_multiplayer_authority():
        # Local player: apply input and send to server
        var input := Input.get_vector("left", "right", "up", "down")
        velocity = input * speed
        move_and_slide()
        send_input.rpc_id(1, input)
    else:
        # Remote player: interpolate to server position
        global_position = global_position.lerp(_server_position, delta * 15.0)

@rpc("any_peer", "unreliable_ordered")
func send_input(input: Vector2) -> void:
    if not multiplayer.is_server():
        return
    # Server processes input authoritatively
    velocity = input * speed
    move_and_slide()
    # Send corrected position to all clients
    sync_position.rpc(global_position)

@rpc("authority", "unreliable_ordered")
func sync_position(pos: Vector2) -> void:
    _server_position = pos
```

### Chat System
```gdscript
@rpc("any_peer", "call_local", "reliable")
func send_chat(message: String) -> void:
    var sender_id: int = multiplayer.get_remote_sender_id()
    var sender_name: String = players.get(sender_id, "Unknown")
    display_chat("[%s] %s" % [sender_name, message])

func display_chat(text: String) -> void:
    $ChatLog.text += text + "\n"
```

---

## Debugging Multiplayer

### Run Multiple Instances
In the editor: Debug > Run Multiple Instances (2-4 windows)

### Logging
```gdscript
func _log(msg: String) -> void:
    var peer_id: int = multiplayer.get_unique_id() if multiplayer.has_multiplayer_peer() else 0
    print("[Peer %d] %s" % [peer_id, msg])
```

### Common Issues
1. **RPC not calling** — Check that the function has `@rpc` annotation and that you're calling `.rpc()` not the function directly
2. **Authority mismatch** — Only the authority can call `@rpc("authority")` functions
3. **Node paths differ** — Ensure node paths are identical on all peers (same names, same tree structure)
4. **Spawner not replicating** — The scene must be registered in MultiplayerSpawner's spawn list
5. **Sync jitter** — Increase replication_interval or add interpolation
