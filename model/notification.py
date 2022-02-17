from pydantic import BaseModel
from typing import Optional

class NotificationModel(BaseModel):
    id:str
    user_id: str
    payload: dict
    sent: bool
    first_modified: Optional[str]
    last_modified: Optional[str]

    @staticmethod
    def to_model(notification_json):
        return NotificationModel(
            id=notification_json["id"],
            user_id=notification_json["userId"],
            payload=notification_json["payload"],
            sent=notification_json["sent"],
            first_modified=notification_json["firstModified"],
            last_modified=notification_json["lastModified"]

        )

    def to_json(self):
        load = {
            "id" : self.id,
            "userId" : self.user_id,
            "payload" : self.payload,
            "sent" : self.sent,
            "firstModified" : self.first_modified,
            "lastModified" : self.last_modified
        }
        return load