import os
from pymongo import MongoClient
from bson.objectid import ObjectId

class AnimalShelterCRUD(object):
    """CRUD operations for Animal collection in MongoDB"""

    def __init__(self, username, password):
        self.username = username
        self.password = password
        HOST = 'nv-desktop-services.apporto.com'
        PORT = 33817
        DB = 'AAC'
        COL = 'animals'
        
        ##Initial Connection
        
        self.client = MongoClient('mongodb://%s:%s@%s:%d' % (username, password, HOST, PORT))
        self.database = self.client['%s' % (DB)]
        self.collection = self.database['%s' % (COL)]

    # Complete this create method to implement the C in CRUD.
    def create(self, data):
        if data is not None:
            result = self.collection.insert_one(data)  # data should be a dictionary
            return result.inserted_id
        else:
            raise Exception("Nothing to save, because data parameter is empty")

    # Method to implement the R in CRUD.
    def read(self, query=None):
        if query is not None:
            data = self.collection.find(query)
            return list(data)
        else:
            data = self.collection.find()
            return list(data)

    def update(self, query, update_data, multiple=False):
        if query is not None and update_data is not None:
            if multiple:
                result = self.collection.update_many(query, {'$set': update_data})
            else:
                result = self.collection.update_one(query, {'$set': update_data})
            return result.modified_count
        else:
            raise Exception("Query empty")

    def delete(self, query):
        if query is not None:
            result = self.collection.delete_many(query)
            return result.deleted_count
        else:
            raise Exception("Query empty")
            
    def searchRecordsByCriteria(self, criteria):
        return list(self.collection.find(criteria))