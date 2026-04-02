from fastapi import APIRouter, WebSocket
from fastapi.responses import HTMLResponse

from domain_gateway.connections.externals.connections.websocket.service import (
    WebSocketManagerDep,
)

ws_router = APIRouter(prefix="/ws", tags=["websocket"])


@ws_router.websocket("")
async def websocket_endpoint(
    websocket: WebSocket, websocket_manager: WebSocketManagerDep
):
    await websocket_manager.add(websocket)


@ws_router.get("/test")
async def websocket_test_page():
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>WebSocket Test Client</title>
        <style>
            body {
                font-family: monospace;
                max-width: 1200px;
                margin: 20px auto;
                padding: 20px;
                background: #1e1e1e;
                color: #d4d4d4;
            }
            .container {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 20px;
            }
            .panel {
                border: 1px solid #444;
                border-radius: 8px;
                padding: 15px;
                background: #252526;
            }
            .messages {
                height: 400px;
                overflow-y: auto;
                border: 1px solid #444;
                border-radius: 4px;
                padding: 10px;
                margin: 10px 0;
                background: #1e1e1e;
            }
            .message {
                margin: 5px 0;
                padding: 5px;
                border-radius: 4px;
            }
            .sent {
                color: #4ec9b0;
                border-left: 3px solid #4ec9b0;
                padding-left: 10px;
            }
            .received {
                color: #ce9178;
                border-left: 3px solid #ce9178;
                padding-left: 10px;
            }
            .error {
                color: #f48771;
                border-left: 3px solid #f48771;
            }
            input, select, button {
                background: #3c3c3c;
                color: #d4d4d4;
                border: 1px solid #555;
                padding: 8px;
                margin: 5px;
                border-radius: 4px;
                font-family: monospace;
            }
            button {
                cursor: pointer;
                background: #0e639c;
            }
            button:hover {
                background: #1177bb;
            }
            .status {
                display: inline-block;
                width: 10px;
                height: 10px;
                border-radius: 50%;
                margin-right: 8px;
            }
            .connected {
                background: #4ec9b0;
                box-shadow: 0 0 5px #4ec9b0;
            }
            .disconnected {
                background: #f48771;
            }
            h3 {
                margin-top: 0;
                color: #dcdcaa;
            }
            hr {
                border-color: #444;
            }
        </style>
    </head>
    <body>
        <h1>🧪 WebSocket Test Client</h1>

        <div class="container">
            <div class="panel">
                <h3>📡 Connection</h3>
                <div>
                    <span id="status-indicator" class="status disconnected"></span>
                    <span id="status-text">Disconnected</span>
                </div>
                <br>
                <button onclick="connect()">🔌 Connect</button>
                <button onclick="disconnect()">❌ Disconnect</button>
                <hr>

                <h3>📤 Subscribe to Topic</h3>
                <input type="text" id="subscription_id" placeholder="Subscription ID (UUID)" style="width: 70%">
                <button onclick="subscribe()">Subscribe</button>

                <h3>📨 Publish Message</h3>
                <input type="text" id="publish_topic" placeholder="Topic (e.g., robot/1/position)" style="width: 70%">
                <br>
                <textarea id="publish_payload" rows="4" placeholder='{"x": 100, "y": 200}' style="width: 95%"></textarea>
                <br>
                <button onclick="publish()">Publish</button>
            </div>

            <div class="panel">
                <h3>💬 Messages</h3>
                <button onclick="clearMessages()">Clear</button>
                <div id="messages" class="messages"></div>

                <h3>📝 Message Templates</h3>
                <button onclick="loadPositionTemplate()">📍 Position Update</button>
                <button onclick="loadStatusTemplate()">⚡ Status Update</button>
            </div>
        </div>

        <script>
            let ws = null;

            function addMessage(type, content, isError = false) {
                const messagesDiv = document.getElementById('messages');
                const messageDiv = document.createElement('div');
                messageDiv.className = `message ${type}`;
                if (isError) messageDiv.classList.add('error');

                const timestamp = new Date().toLocaleTimeString();
                messageDiv.innerHTML = `<strong>[${timestamp}]</strong> ${type.toUpperCase()}: ${JSON.stringify(content, null, 2)}`;
                messagesDiv.appendChild(messageDiv);
                messagesDiv.scrollTop = messagesDiv.scrollHeight;
            }

            function updateStatus(connected) {
                const indicator = document.getElementById('status-indicator');
                const text = document.getElementById('status-text');
                if (connected) {
                    indicator.className = 'status connected';
                    text.textContent = 'Connected';
                } else {
                    indicator.className = 'status disconnected';
                    text.textContent = 'Disconnected';
                }
            }

            function connect() {
                if (ws && ws.readyState === WebSocket.OPEN) {
                    addMessage('system', 'Already connected', false);
                    return;
                }

                // Use wss:// for HTTPS, ws:// for HTTP
                const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
                const wsUrl = `${protocol}//${window.location.host}/ws`;

                addMessage('system', `Connecting to ${wsUrl}...`, false);
                ws = new WebSocket(wsUrl);

                ws.onopen = () => {
                    addMessage('system', 'Connected successfully!', false);
                    updateStatus(true);
                };

                ws.onmessage = (event) => {
                    try {
                        const data = JSON.parse(event.data);
                        addMessage('received', data);
                    } catch (e) {
                        addMessage('received', event.data);
                    }
                };

                ws.onerror = (error) => {
                    addMessage('error', 'WebSocket error occurred', true);
                    console.error('WebSocket error:', error);
                };

                ws.onclose = (event) => {
                    addMessage('system', `Disconnected: ${event.reason || 'No reason provided'}`, false);
                    updateStatus(false);
                    ws = null;
                };
            }

            function disconnect() {
                if (ws) {
                    ws.close();
                    ws = null;
                    addMessage('system', 'Disconnecting...', false);
                } else {
                    addMessage('system', 'Not connected', false);
                }
            }

            function subscribe() {
                if (!ws || ws.readyState !== WebSocket.OPEN) {
                    addMessage('error', 'Not connected to WebSocket server', true);
                    return;
                }

                const subscriptionId = document.getElementById('subscription_id').value;
                if (!subscriptionId) {
                    addMessage('error', 'Please enter a Subscription ID (UUID)', true);
                    return;
                }

                const message = {
                    id: subscriptionId
                };

                ws.send(JSON.stringify(message));
                addMessage('sent', message);
            }

            function publish() {
                if (!ws || ws.readyState !== WebSocket.OPEN) {
                    addMessage('error', 'Not connected to WebSocket server', true);
                    return;
                }

                const topic = document.getElementById('publish_topic').value;
                const payloadStr = document.getElementById('publish_payload').value;

                if (!topic) {
                    addMessage('error', 'Please enter a topic', true);
                    return;
                }

                if (!payloadStr) {
                    addMessage('error', 'Please enter a payload', true);
                    return;
                }

                try {
                    const payload = JSON.parse(payloadStr);
                    const message = {
                        topic: topic,
                        payload: payload
                    };
                    ws.send(JSON.stringify(message));
                    addMessage('sent', message);
                } catch (e) {
                    addMessage('error', `Invalid JSON payload: ${e.message}`, true);
                }
            }

            function clearMessages() {
                document.getElementById('messages').innerHTML = '';
                addMessage('system', 'Messages cleared', false);
            }

            function loadPositionTemplate() {
                document.getElementById('publish_topic').value = 'robot/1/position';
                document.getElementById('publish_payload').value = JSON.stringify({
                    x: Math.floor(Math.random() * 1000),
                    y: Math.floor(Math.random() * 1000),
                    timestamp: new Date().toISOString()
                }, null, 2);
            }

            function loadStatusTemplate() {
                document.getElementById('publish_topic').value = 'robot/1/status';
                document.getElementById('publish_payload').value = JSON.stringify({
                    battery: Math.floor(Math.random() * 100),
                    status: ['idle', 'moving', 'charging'][Math.floor(Math.random() * 3)],
                    timestamp: new Date().toISOString()
                }, null, 2);
            }

            // Auto-connect on page load (optional)
            // window.addEventListener('load', () => { setTimeout(connect, 500); });
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)
