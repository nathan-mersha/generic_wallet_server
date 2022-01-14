from model.user import UserModel
from datetime import datetime

import configparser
import pymongo


class UserModelDAL:
    DATABASE_NAME = "genericWalletDB"
    COLLECTION_NAME = "user"

    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read("./cred/config.ini")

        # database connection string
        data_base_connection_str = str(self.config['mongodb']['database_url'])
        client = pymongo.MongoClient(data_base_connection_str, serverSelectionTimeoutMS=5000)
        db = client[self.DATABASE_NAME]
        self.collection = db[self.COLLECTION_NAME]

    async def create(self, user_model: UserModel):
        user_model.first_modified = str(datetime.now().isoformat())
        user_model.last_modified = str(datetime.now().isoformat())
        return self.collection.insert_one(UserModel.to_json(user_model))

    def read(self, query = {}, limit = 24, sort = 'firstModified', sort_type = pymongo.DESCENDING):
        data = []
        response = self.collection.find(query).limit(limit).sort(sort, sort_type)
        for document in response:
            user_model = UserModel.to_model(document)
            data.append(user_model)
        return data


    def update(self, query, update_data):
        update_data["lastModified"] = str(datetime.now().isoformat())
        set_update = {"$set": update_data}
        return self.collection.update_one(query, set_update)


    def delete(self):
        pass
