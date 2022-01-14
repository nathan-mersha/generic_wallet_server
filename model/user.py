from datetime import datetime
from pydantic import BaseModel
from typing import Optional


class UserModel(BaseModel):
    id: Optional[str] = 'none'
    wallet_id: Optional[str] = 'none'
    available_balance: Optional[float] = 0
    name: str
    email: str
    password: str
    payload: Optional[dict] = {}
    first_modified: Optional[str] = str(datetime.now().isoformat())
    last_modified: Optional[str] = str(datetime.now().isoformat())

    @staticmethod
    def to_model(user_json):
        return UserModel(
            id=user_json["id"],
            wallet_id=user_json["walletId"],
            available_balance=user_json["availableBalance"],
            name=user_json["name"],
            email=user_json["email"],
            password=user_json["password"],
            payload=user_json["payload"],
            first_modified=user_json["firstModified"],
            last_modified=user_json["lastModified"]
        )

    def to_json(self):
        load = {
            "id": self.id,
            "walletId": self.wallet_id,
            "availableBalance": self.available_balance,
            "name" : self.name,
            "email" : self.email,
            "password" : self.password,
            "payload" : self.payload,
            "firstModified": self.first_modified,
            "lastModified": self.last_modified
        }

        return load

class LoginModel(BaseModel):
    email: str
    password: str        

class ForgotPasswordModel(BaseModel):
    email: str    

class ResetPasswordModel(BaseModel):
    email: str
    reset_code: str
    new_password: str

class ChangePasswordModel(BaseModel):
    old_password: str
    new_password: str

class UpdateUserModel(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None

    def to_json(self):
        load = {}
        if self.name != None:
            load["name"] = self.name

        if self.email != None:
            load["email"] = self.email

        return load


