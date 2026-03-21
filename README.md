# API Endpoints

## Translation Server

Il Translation Server funge da bridge tra MQTT e HTTP. Sono in discussione tre alternative per la comunicazione.

### Opzione A — SSE + REST

SSE per la subscribe, REST per la publish.

La subscribe può essere strutturata in due modi:

**Path-based:**
```
GET /subscription/robots/position
GET /subscription/robots/{robot_id}/position
GET /subscription/robots/neighbor
GET /subscription/robots/{robot_id}/neighbor
GET /subscription/robots/movement
GET /subscription/robots/{robot_id}/movement
GET /subscription/leader
GET /subscription/sensing
```

**Query params** (permette di sottoscriversi a più topic con una sola connessione):
```
GET /subscription?topic=robots/position
GET /subscription?topic=robots/{robot_id}/position
GET /subscription?topic=leader
GET /subscription?topic=robots/position&topic=leader
```

Publish:
```
POST /publish/robots/{robot_id}/position
POST /publish/robots/{robot_id}/neighbor
POST /publish/robots/{robot_id}/movement
POST /publish/leader
POST /publish/sensing
```

---

### Opzione B — WebSocket

Unico protocollo per subscribe e publish. La subscribe usa query params per permettere più topic su una singola connessione, la publish usa path espliciti.

```
# subscribe
WS /ws/subscription?topic=robots/position
WS /ws/subscription?topic=robots/{robot_id}/position
WS /ws/subscription?topic=leader
WS /ws/subscription?topic=robots/position&topic=leader

# publish
WS /ws/publish/robots/{robot_id}/position
WS /ws/publish/robots/{robot_id}/neighbor
WS /ws/publish/robots/{robot_id}/movement
WS /ws/publish/leader
WS /ws/publish/sensing
```

---

### Opzione C — Ibrido SSE + WebSocket

SSE per la subscribe, WebSocket per la publish. Utile se i client che pubblicano lo fanno frequentemente — WebSocket riduce l'overhead rispetto a un POST per ogni messaggio.

```
# subscribe (SSE)
GET /subscription?topic=robots/position
GET /subscription?topic=robots/{robot_id}/position
GET /subscription?topic=leader
GET /subscription?topic=robots/position&topic=leader

# publish (WebSocket)
WS /ws/publish/robots/{robot_id}/position
WS /ws/publish/robots/{robot_id}/neighbor
WS /ws/publish/robots/{robot_id}/movement
WS /ws/publish/leader
WS /ws/publish/sensing
```

---

## Offloading Manager

### Stato offloading (REST)

```
GET  /                    # stato di offloading di tutti i robot
GET  /{robot_id}          # stato di offloading di un robot specifico
POST /{robot_id}          # aggiorna lo stato di offloading di un robot
GET  /system-stress       # carico attuale del sistema
```

### Istruzioni ai moduli (SSE)

L'offloading manager notifica i moduli di processing su quali robot devono computare. Sono in discussione due strutture:

**Path-based:** (un unico endpoint, il modulo dichiara la propria capability):
```
GET /offloading/stream?capability=position
GET /offloading/stream?capability=neighbor
GET /offloading/stream?capability=movement
GET /offloading/stream?capability=position&capability=movement
```

**Query params** (un endpoint dedicato per capability):
```
GET /offloading/position/stream
GET /offloading/neighbor/stream
GET /offloading/movement/stream
```

### Comunicazione con i robot (WebSocket)

Canale bidirezionale tra l'offloading manager e un singolo robot. Il server può richiedere al robot di computare localmente, il robot può accettare, rifiutare o notificare che non è più in grado di farlo.

```
WS /ws/offloading/robots/{robot_id}
```
