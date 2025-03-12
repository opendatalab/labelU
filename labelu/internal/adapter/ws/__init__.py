from fastapi import FastAPI

from labelu.internal.adapter.ws.sample import task_ws_endpoint

def add_ws_router(app: FastAPI):
    app.add_api_websocket_route("/ws/task/{task_id}/{sample_id}", task_ws_endpoint)