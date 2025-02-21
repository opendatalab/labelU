from fastapi import Depends, WebSocket, WebSocketDisconnect
from loguru import logger
from pydantic import BaseModel

from labelu.internal.clients.ws import sampleConnections
from labelu.internal.common.websocket import ConnectionData
from labelu.internal.dependencies.user import verify_ws_token
    
class TaskWsPayload(BaseModel):
    task_id: int
    user_id: int
    username: str
    
class TaskSampleWsPayload(TaskWsPayload):
    sample_id: int
    
def get_task_sample_connection_payloads(conns: ConnectionData):
    result = []
    
    if not conns:
        return {
            "type": "active_connections",
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
        "type": "active_connections",
        "data": result
    }
    
async def task_sample_ws_endpoint(websocket: WebSocket, task_id: int, sample_id: int, user=Depends(verify_ws_token)):
    if not user:
        return
    
    client_id = f"{task_id}_{sample_id}"
    
    async def tell_others():
        connections = sampleConnections.active_connections
        current_connection = connections.get(client_id, [])
        sample_payload = get_task_sample_connection_payloads(current_connection)
        
        await sampleConnections.send_message(sample_payload, client_id)
    
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
        
        while True:
            await websocket.receive_text()
            
    except WebSocketDisconnect:
        await sampleConnections.disconnect(websocket, client_id)
        await tell_others()
    except Exception as e:
        logger.error(f"WebSocket error for user {client_id}: {e}")
        await sampleConnections.disconnect(websocket, client_id)
        await tell_others()