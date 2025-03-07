from typing import List
from fastapi import Depends, WebSocket, WebSocketDisconnect
from loguru import logger
from pydantic import BaseModel

from labelu.internal.clients.ws import sampleConnections, taskConnections
from labelu.internal.common.websocket import ConnectionData
from labelu.internal.dependencies.user import verify_ws_token

class CollaboratorWsPayload(BaseModel):
    user_id: int
    username: str
    sample_id: int
    
class TaskWsPayload(BaseModel):
    task_id: int
    user_id: int
    username: str
    collaborators: List[CollaboratorWsPayload] = []
    
class TaskSampleWsPayload(BaseModel):
    task_id: int
    user_id: int
    username: str
    sample_id: int
    
def get_task_connection_payloads(conns: ConnectionData):    
    if not conns:
        return {
            "type": "peers",
            "data": {
                "collaborators": [],
                "connections": []
            }
        }
    
    connections = []
    collaborators = []
    
    for conn in conns:
        connections.append({
            "task_id": conn.data.task_id,
            "user_id": conn.data.user_id,
            "username": conn.data.username
        })
    
    for _, sample_conns in sampleConnections.active_connections.items():
        if sample_conns[0].data.task_id == conns[0].data.task_id:
            for sample_conn in sample_conns:
                # The first connector in the sample connection is the annotator, and the others can not annotate
                collaborators.append({
                    "user_id": sample_conn.data.user_id,
                    "username": sample_conn.data.username,
                    "sample_id": sample_conn.data.sample_id
                })
        
    return {
        "type": "peers",
        "data": {
            "collaborators": collaborators,
            "connections": connections
        }
    }
    
def get_task_sample_connection_payloads(conns: ConnectionData):
    result = []
    
    if not conns:
        return {
            "type": "peers",
            "data": []
        }
    
    for conn in conns:
        result.append({
            "task_id": conn.data.task_id,
            "user_id": conn.data.user_id,
            "username": conn.data.username,
            "sample_id": conn.data.sample_id,
        })
        
    return {
        "type": "peers",
        "data": result
    }

async def task_ws_endpoint(websocket: WebSocket, task_id: int, user=Depends(verify_ws_token)):
    if not user:
        return
    
    client_id = f"{task_id}"
    
    async def tell_others():
        connections = taskConnections.active_connections
        current_connection = connections.get(client_id, [])
        task_payload = get_task_connection_payloads(current_connection)
        
        await taskConnections.send_message(task_payload, client_id)
    
    try:
        await taskConnections.connect(
            websocket,
            client_id,
            data=TaskWsPayload(
                task_id=task_id,
                user_id=user.id,
                username=user.username
            )
        )
        await tell_others()
        
        while True:
            await websocket.receive_text()
            
    except WebSocketDisconnect:
        await taskConnections.disconnect(websocket, client_id)
        await tell_others()
    except Exception as e:
        logger.error(f"WebSocket error for user {client_id}: {e}")
        await taskConnections.disconnect(websocket, client_id)
        await tell_others()
    
async def task_sample_ws_endpoint(websocket: WebSocket, task_id: int, sample_id: int, user=Depends(verify_ws_token)):
    if not user:
        return
    
    client_id = f"{task_id}_{sample_id}"
    
    async def tell_others():
        connections = sampleConnections.active_connections
        current_connection = connections.get(client_id, [])
        sample_payload = get_task_sample_connection_payloads(current_connection)
        
        await sampleConnections.send_message(sample_payload, client_id)
    
    async def tell_others_someone_leaved():
        await sampleConnections.send_message({
            "type": "leave",
            "data": {
                "task_id": task_id,
                "user_id": user.id,
                "username": user.username,
                "sample_id": sample_id
            },
        }, client_id)
    
    async def tell_other_task_connections():
        connections = taskConnections.active_connections
        current_connection = connections.get(f"{task_id}", [])
        task_payload = get_task_connection_payloads(current_connection)
        
        await taskConnections.send_message(task_payload, f"{task_id}")
    
    try:
        await sampleConnections.connect(
            websocket,
            client_id,
            data=TaskSampleWsPayload(
                task_id=task_id,
                sample_id=sample_id,
                user_id=user.id,
                username=user.username
            )
        )
        await tell_others()
        await tell_other_task_connections()
        
        while True:
            await websocket.receive_text()
            
    except WebSocketDisconnect:
        await sampleConnections.disconnect(websocket, client_id)
        await tell_others()
        await tell_others_someone_leaved()
        await tell_other_task_connections()
        
    except Exception as e:
        logger.error(f"WebSocket error for user {client_id}: {e}")
        await sampleConnections.disconnect(websocket, client_id)
        await tell_others()
        await tell_others_someone_leaved()
        await tell_other_task_connections()