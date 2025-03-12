from enum import Enum
import time
from typing import Any, Dict, List
import uuid
from fastapi import WebSocket
from loguru import logger
import asyncio
from dataclasses import dataclass

from pydantic import BaseModel

HEARTBEAT_INTERVAL = 30
HEARTBEAT_TIMEOUT = 60

class MessageType(str, Enum):
    PEERS = "peers"
    PING = "ping"
    PONG = "pong"
    UPDATE = "update"

class Message(BaseModel):
    type: MessageType
    data: Any = None

@dataclass
class ConnectionData:
    id: str = None
    ws: WebSocket = None
    data: Any = None
    heartbeat_task: asyncio.Task = None
    last_heartbeat: float = time.time()
    
    def update_heartbeat(self):
        self.last_heartbeat = time.time()

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, Dict[str, ConnectionData]] = {}
        
    def _get_connection(self, client_id: str, connection_id: uuid.UUID) -> ConnectionData:
        if client_id in self.active_connections:
            return self.active_connections[client_id].get(connection_id)
        
        return None
            
    async def _heartbeat(self, client_id: str, connection_id: uuid.UUID):
        while True:
            try:
                await asyncio.sleep(HEARTBEAT_INTERVAL)
                
                # Send ping message
                connection = self._get_connection(client_id, connection_id)
                
                if not connection:
                    break
                
                await self.send_message(client_id, connection_id, Message(type=MessageType.PING))
                
                # Check if heartbeat timeout
                if connection and time.time() - connection.last_heartbeat > HEARTBEAT_TIMEOUT:
                    logger.error(f"Heartbeat timeout for client {connection.data.username}")
                    await self.disconnect(client_id, connection.ws)
                    break
                
            except Exception as e:
                logger.error(f"Error in heartbeat for client {client_id}: {e}")
                break
            
    async def connect(self, client_id: str, websocket: WebSocket, data: Any = None) -> ConnectionData:
        await websocket.accept()
        
        if client_id not in self.active_connections:
            self.active_connections[client_id] = []
            
        logger.info(f"Client {client_id} connected")
        id = str(uuid.uuid4())
        connection_data = ConnectionData(
            id=id,
            ws=websocket,
            data=data,
            last_heartbeat=time.time(),
            heartbeat_task=asyncio.create_task(self._heartbeat(client_id, id)),
        )
        
        if not self.active_connections[client_id]:
            self.active_connections[client_id] = {}
            
        self.active_connections[client_id][id] = connection_data
        
        return connection_data
    
    async def disconnect(self, client_id: str, websocket: WebSocket):
        if client_id not in self.active_connections:
            return
        
        connection_to_remove = None
        for connection_id, connection in self.active_connections[client_id].items():
            if connection.ws == websocket:
                connection.heartbeat_task.cancel()
                connection_to_remove = connection
                logger.info(f"Client {client_id} disconnected")
                break
        
        if connection_to_remove is not None:
            del self.active_connections[client_id][connection_to_remove.id]
        
        if client_id in self.active_connections and not self.active_connections[client_id]:
            del self.active_connections[client_id]
        
    async def send_message(self, client_id: str, conn_id: uuid.UUID | None = None, message: Message = None):
        if not conn_id:
            if client_id in self.active_connections:
                for connection in self.active_connections[client_id].values():
                    await connection.ws.send_json(message.dict())
        else:
            connection = self._get_connection(client_id, conn_id)
            if connection:
                await connection.ws.send_json(message.dict())