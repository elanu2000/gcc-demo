from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from urllib.parse import quote_plus
import json

class MongoDb:
    def __init__(self):
        self.establish_connection()
        
    def establish_connection(self):
        username = quote_plus("elanu2000")
        password = quote_plus("Toiahb4psWjJiCUN")
        uri = "mongodb+srv://" + username + ":" + password + "@gcc.levemnn.mongodb.net/?retryWrites=true&w=majority"
        self.client = MongoClient(uri, server_api=ServerApi('1'))
        self.db = self.client["GCC"]

    def get_collection(self, collection):
        collection = []
        documents = self.db[collection].find()
        for doc in documents:
            dict = {}
            for key in doc:
                if key != "_id":
                    dict[key] = doc[key]
            collection.append(dict)
        return collection
    
    def get_element(self, collection, key, value):
        return self.db[collection].find_one({key: value})
    
    def write_element(self, collection, document):
        self.db[collection].insert_one(document)