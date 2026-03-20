Translation Server

SSE

# subscribe (SSE)
GET /subscription/robots/position
GET /subscription/robots/{robot_id}/position
GET /subscription/robots/neighbor
GET /subscription/robots/{robot_id}/neighbor
GET /subscription/robots/movement (o move per simmetria con mqtt)
GET /subscription/robots/{robot_id}/movement (o move per simmetria con mqtt)
GET /subscription/leader
GET /subscription/sensing

# publish (REST)
POST /publish/robots/{robot_id}/position
POST /publish/robots/{robot_id}/neighbor
POST /publish/robots/{robot_id}/movement (o move per simmetria con mqtt)
POST /publish/leader
POST /publish/sensing

WebSocket

# subscribe (WebSocket)
ws://host/ws/subscription?topic=robots/position
ws://host/ws/subscription?topic=robots/123/position
ws://host/ws/subscription?topic=leader
ws://host/ws/subscription?topic=robots/position&topic=leader

# publish (WebSocket)
ws://host/ws/publish/robots/{robot_id}/position
ws://host/ws/publish/robots/{robot_id}/neighbor
ws://host/ws/publish/robots/{robot_id}/movement
ws://host/ws/publish/leader
ws://host/ws/publish/sensing

Offloading Manager

questi rimarrebbero uguali:

# default (REST)
GET   /
GET   /{robot_id}
POST  /{robot_id}

# stress (REST)
GET /system-stress

invece per le comunicazioni si potrebbe adottare sse al posto di webhook:

prima possibilità:

GET /instructions/stream?capability=position&capability=movement
GET /instructions/stream?capability=neighbor

seconda possibilità:

GET /instructions/position/stream
GET /instructions/neighbor/stream
GET /instructions/movement/stream

seconda possibilità:

tutto ws TODOOOOOOOO

# robot
