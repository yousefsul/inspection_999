import datetime

from bson import ObjectId
from pymongo import MongoClient

MONGO_CLIENT = "mongodb://yousef:Ys2021xch@209.151.150.58:63327/?authSource=admin&readPreference=primary&appname" \
               "=MongoDB%20Compass&ssl=false"


class ConnectMongoDB:
    """
    connect to devDB and client database
    define the clients_collection,visits_collection,claims_collection as none
    """

    def __init__(self):
        try:
            self.mongo_client = MongoClient(MONGO_CLIENT)
            self.db = self.mongo_client.client_2731928905_DB
            self.ack_collection = None
            self.index_collection = None
            self.dict_837_collection = None
        except ConnectionError:
            print(ConnectionError, "connection error have been occured")

    def connect_to_ack_collection(self):
        self.ack_collection = self.db.ack_coll

    def connect_to_837_collection(self):
        self.dict_837_collection = self.db['837_dict_coll']

    def connect_to_index_collection(self):
        self.index_collection = self.db.index_coll

    def insert_to_ack_collection(self, result):
        try:
            self.ack_collection.insert(result)
        except Exception as e:
            print("An Exception occurred ", e)

    def get_indexs(self, transaction_type):
        return self.index_collection.find(
            {"$and": [{"837_index.header_section.current_status.status": "new"}, {'837_index.ST.01': transaction_type}]
             })

    def add_999_index(self, param, ack_index):
        self.index_collection.find_one_and_update(
            {"_id": param},
            {"$set":
                 {"999_index": ack_index}
             }
        )

    def update_index_history_status_collection(self, param):
        self.index_collection.update_one(
            {"_id": param},
            {"$push": {
                "837_index.header_section.status_history": {
                    "status": "matched",
                    "date": {
                        "date": datetime.datetime.now().date().strftime("%Y%m%d"),
                        "time": datetime.datetime.now().time().strftime("%H:%M:%S")
                    }
                }
            }}
        )

    def update_index_current_status(self, param):
        self.index_collection.find_and_modify(
            query={"_id": param},
            update={"$set": {
                "837_index.header_section.current_status.status": "matched",
                "837_index.header_section.current_status.date": {
                    "date": datetime.datetime.now().date().strftime("%Y%m%d"),
                    "time": datetime.datetime.now().time().strftime("%H:%M:%S")
                }}
            },
            upsert=True
        )

    def update_837_history_status_collection(self, param):
        self.dict_837_collection.update_one(
            {"header_section.id": param},
            {"$push": {
                "header_section.status_history": {
                    "status": "matched",
                    "date": {
                        "date": datetime.datetime.now().date().strftime("%Y%m%d"),
                        "time": datetime.datetime.now().time().strftime("%H:%M:%S")
                    }
                }
            }}
        )

    def update_837_current_status(self, param):
        self.dict_837_collection.find_and_modify(
            query={"header_section.id": param},
            update={"$set": {
                "header_section.current_status.status": "matched",
                "header_section.current_status.date": {
                    "date": datetime.datetime.now().date().strftime("%Y%m%d"),
                    "time": datetime.datetime.now().time().strftime("%H:%M:%S")
                }}
            },
            upsert=True
        )
