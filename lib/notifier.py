from collections import UserDict
from datetime import datetime
from typing import Dict, List
import uuid
from starlette.websockets import WebSocket
import json
from dal.notification import NotificationModelDAL

from model.notification import NotificationModel

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[Dict] = []
        self.notification_model_dal = NotificationModelDAL()

    async def connect(self, websocket: WebSocket):
        print("Socket connected ----->")
        await websocket.accept()
        userId = await websocket.receive_text()
        data = {
            "websocket" : websocket,
            "userId" : userId
        }
        self.active_connections.append(data)

    def disconnect(self, websocket: WebSocket):
        print("Socket disconnected ----->")
        for active_connection in self.active_connections:
            if active_connection["websocket"] == websocket:
                self.active_connections.remove(active_connection)

    async def send_personal_message(self, message: str, userId: str):      
        print(f"message is : {message}")
        print(f"user id is : {userId}")  
        for active_connection in self.active_connections:
            if active_connection["userId"] == userId:
                res = await active_connection["websocket"].send_text(message)
                if res == "None": # user is not connected, save to db to notify the next time he does
                    notification_data = NotificationModel(
                        id=str(uuid.uuid4()),
                        user_id=userId,
                        payload= message, # this message is a json string
                        sent=False,
                        first_modified=str(datetime.now().isoformat()),
                        last_modified=str(datetime.now().isoformat()))

                    await self.notification_model_dal.create(notification_data)    
              

    async def broadcast(self, message: str):
        print("Broadcasting ------>")
        for connection in self.active_connections:
            await connection["websocket"].send_text(message)
