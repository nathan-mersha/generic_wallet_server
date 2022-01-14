from pymongo.database import Database
from dal.user import UserModelDAL
from model.user import UserModel
from model.transaction import TransactionModel
from dal.user import UserModelDAL

from datetime import datetime
import configparser
import pymongo

class TransactionModelDAL:
    DATABASE_NAME = "genericWalletDB"
    COLLECTION_NAME = "transaction"

    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read("./cred/config.ini")

        # database connection string
        data_base_connection_str = str(self.config['mongodb']['database_url'])
        self.client = pymongo.MongoClient(data_base_connection_str, serverSelectionTimeoutMS=5000)
        self.db = self.client[self.DATABASE_NAME]
        self.transaction_collection = self.db[self.COLLECTION_NAME]
        self.user_collection = self.db[UserModelDAL.COLLECTION_NAME]

    async def create(self, transactionModel: TransactionModel):
        with self.client.start_session() as session:
            with session.start_transaction():
                # updating sender's account
                sender_query = {"id" : transactionModel.from_user["id"]}
                sender_update = {"$inc" : {"availableBalance" : transactionModel.amount * -1}}
                self.user_collection.update_one(sender_query, sender_update)

                # update receivers account
                receiver_query = {"id" : transactionModel.to_user["id"]}
                receiver_update = {"$inc" : {"availableBalance" : transactionModel.amount}}
                self.user_collection.update_one(receiver_query, receiver_update)

                # create transaction document
                return self.transaction_collection.insert_one(TransactionModel.to_json(transactionModel))

    def read(self, query = {}, limit = 24, sort = "firstModified", sort_type=pymongo.DESCENDING):
        data = []
        response = self.transaction_collection.find(query).limit(limit).sort(sort, sort_type)
        for document in response:
            transaction_model = TransactionModel.to_model(document)
            data.append(transaction_model)
        return data               