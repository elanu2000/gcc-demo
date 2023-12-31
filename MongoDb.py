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
    
    def get_element_by_query(self, collection, query):
        return self.db[collection].find_one(query)
    
    def get_element(self, collection, key, value):
        return self.db[collection].find_one({key: value})
    
    def write_element(self, collection, document):
        self.db[collection].insert_one(document)

    def update_document(self, collection, criteria_key, criteria_value, key_to_update, value_to_update):
        self.db[collection].update_one({criteria_key: criteria_value}, {"$set": {key_to_update : value_to_update}})

    def update_document_by_query(self, collection, critera_query, to_update_query):
        self.db[collection].update_one(critera_query, {"$set": to_update_query})