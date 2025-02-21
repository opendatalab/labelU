from typing import Any, Dict, List
from fastapi import WebSocket
from loguru import logger
from dataclasses import dataclass

@dataclass
class ConnectionData:
    ws: WebSocket
    data: Any = None

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[ConnectionData]] = {}
    
    async def connect(self, websocket: WebSocket, client_id: str, data: Any = None):
        await websocket.accept()
        
        if client_id not in self.active_connections:
            self.active_connections[client_id] = []
            
        logger.info(f"Client {client_id} connected")
        self.active_connections[client_id].append(ConnectionData(ws=websocket, data=data))
    
    async def disconnect(self, websocket: WebSocket, client_id: str):
        if client_id in self.active_connections:
            self.active_connections[client_id] = [
                connection for connection in self.active_connections[client_id]
                if connection.ws != websocket
            ]
            
            if not self.active_connections[client_id]:
                del self.active_connections[client_id]
                
            logger.info(f"Client {client_id} disconnected")
    
    async def send_message(self, message: dict, client_id: str):
        if client_id in self.active_connections:
            for connection in self.active_connections[client_id]:
                await connection.ws.send_json(message)
    
    async def broadcast(self, message: dict, exclude: str = None):
        for client_id, connections in self.active_connections.items():
            if client_id != exclude:
                for connection in connections:
                    await connection.ws.send_json(message)
                    
    async def send_personal_message(self, message: dict, client_id: str):
        if client_id in self.active_connections:
            for connection in self.active_connections[client_id]:
                await connection.ws.send_json(message)