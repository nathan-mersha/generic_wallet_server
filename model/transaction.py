from curses import ALL_MOUSE_EVENTS
from pydantic import BaseModel
from typing import Optional


class TransactionModel(BaseModel):
    id: str
    amount: float
    payload: Optional[dict] = {}
    from_user: dict
    to_user: dict
    trn_type: str # request, transfer
    first_modified: Optional[str]
    last_modified: Optional[str]

    @staticmethod
    def to_model(transaction_json):
        return TransactionModel(
            id=transaction_json["id"],
            amount=transaction_json["amount"],
            payload=transaction_json["payload"],
            from_user=transaction_json["fromUser"],
            to_user=transaction_json["toUser"],
            trn_type=transaction_json["trnType"],
            first_modified=transaction_json["firstModified"],
            last_modified=transaction_json["lastModified"]
        )

    def to_json(self):
        load = {
            "id": self.id,
            "amount" : self.amount,
            "payload" : self.payload,
            "fromUser": self.from_user,
            "toUser" : self.to_user,
            "trnType" : self.trn_type,
            "firstModified": self.first_modified,
            "lastModified": self.last_modified
        }

        return load


class SendMoneyModel(BaseModel):
    amount: float
    payload: Optional[dict] = {}
    to_user_email: str

class RequestMoneyModel(BaseModel):
    amount: float
    payload: Optional[dict] = {}
    to_user_email: str    