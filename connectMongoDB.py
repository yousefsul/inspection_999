import datetime
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
            self.db = self.mongo_client.v6ogx8cvxqfk_DB
            self.test_999_collection = None
            self.info_999_collection = None
        except ConnectionError:
            print(ConnectionError, "connection error have been occured")

    def connect_to_test_999_collection(self):
        self.test_999_collection = self.db.TEST_999

    def insert_to_test_999_collection(self, result):
        try:
            self.test_999_collection.insert(result)
        except Exception as e:
            print("An Exception occurred ", e)

    def connect_to_999_collection(self):
        self.info_999_collection = self.db.index_999

    def insert_to_999_collection(self, result):
        try:
            self.info_999_collection.insert(result)
        except Exception as e:
            print("An Exception occurred ", e)
