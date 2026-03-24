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
GET /subscription/position?topic=robots
GET /subscription/position?topic=robots&topic=leader
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
WS /ws/subscription/position?topic=robots
WS /ws//subscription/position?topic=robots&topic=leader

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
GET /subscription/position?topic=robots
GET /subscription/position?topic=robots&topic=leader

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
PUT /{robot_id}          # aggiorna lo stato di offloading di un robot
GET  /system-stress       # carico attuale del sistema
```
### Comunicazione con altri moduli (WebSocket)

Canali weebsoket per permettere comunicazione con i vari moduli, il server manda aggiornamenti sullo stato dei robot per i quali devono compiere calcoli 

```
WS /ws/position
WS /ws/aggregate
WS /ws/neighboor
```


### Comunicazione con i robot (WebSocket)

Canale bidirezionale tra l'offloading manager e un singolo robot. Il server può richiedere al robot di computare localmente, il robot può accettare, rifiutare o notificare che non è più in grado di farlo.

```
# Server initiated
Server ---"compute locally"---> Robot
Robot  ---"accept/deny"-------> Server

# Robot initiated  
Robot  ---"can't compute"-----> Server
Server ---"acknowledged"------> Robot
```

```
WS /ws/robots/{robot_id}
```
il nome puo essere senno 
```
WS /ws/{robot_id}
```

richieste di offloading da parte robot possono avvennire sia tramite websocket che traminte l'endopint prenisposto rest "PUT /{robot_id} " dove passano tutte il resto delle richiete provenienti dai vari moduli.


