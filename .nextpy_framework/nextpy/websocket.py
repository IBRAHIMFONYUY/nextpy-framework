"""
NextPy WebSocket Support
Real-time communication with clients
"""

from fastapi import WebSocket
from typing import Set, Dict, Callable, Any
import json


class ConnectionManager:
    """Manage WebSocket connections"""
    
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
        self.subscribers: Dict[str, Set[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket):
        """Accept new connection"""
        await websocket.accept()
        self.active_connections.add(websocket)
    
    async def disconnect(self, websocket: WebSocket):
        """Remove connection"""
        self.active_connections.discard(websocket)
        for subs in self.subscribers.values():
            subs.discard(websocket)
    
    async def broadcast(self, message: Dict[str, Any]):
        """Send message to all connections"""
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                pass
    
    async def subscribe(self, websocket: WebSocket, channel: str):
        """Subscribe connection to channel"""
        if channel not in self.subscribers:
            self.subscribers[channel] = set()
        self.subscribers[channel].add(websocket)
    
    async def publish(self, channel: str, message: Dict[str, Any]):
        """Publish message to channel subscribers"""
        if channel in self.subscribers:
            for connection in self.subscribers[channel]:
                try:
                    await connection.send_json(message)
                except:
                    pass


# Global manager instance
manager = ConnectionManager()


async def handle_websocket(websocket: WebSocket):
    """Handle WebSocket connection"""
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Route message to appropriate handler
            msg_type = message.get("type")
            if msg_type == "subscribe":
                await manager.subscribe(websocket, message.get("channel"))
            elif msg_type == "publish":
                await manager.publish(message.get("channel"), message.get("payload"))
            elif msg_type == "broadcast":
                await manager.broadcast(message.get("payload"))
    except:
        pass
    finally:
        await manager.disconnect(websocket)
