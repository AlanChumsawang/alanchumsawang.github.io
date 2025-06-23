import os
import logging
from pymongo import MongoClient
from bson.objectid import ObjectId


class MongoDBConnection:
    def __init__(self, host, port, db_name, client=None):
        self.host = host
        self.port = port
        self.db_name = db_name
        self.client = client or MongoClient(f'mongodb://{self.host}:{self.port}')

    def connect(self):
        try:
            logging.info("MongoDB connection established.")
            return self.client[self.db_name]
        except Exception as e:
            logging.error(f"Failed to connect to MongoDB: {e}")
            raise

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class AnimalShelterCRUD:
    def __init__(self, db_connection: MongoDBConnection, collection_name='animals'):
        self.db_connection = db_connection
        self.collection_name = collection_name
        self.database = self.db_connection.connect()
        self.collection = self.database[self.collection_name]

    def create(self, data):
        if data is not None:
            try:
                result = self.collection.insert_one(data)
                logging.info(f"Document inserted with ID: {result.inserted_id}")
                return result.inserted_id
            except Exception as e:
                logging.error(f"Error during create operation: {e}")
                raise
        else:
            logging.warning("Create operation failed: data parameter is empty")
            raise Exception("Nothing to save, because data parameter is empty")

    def read(self, query=None):
        try:
            if query is not None:
                data = self.collection.find(query)
            else:
                data = self.collection.find()
            logging.info("Read operation successful.")
            return list(data)
        except Exception as e:
            logging.error(f"Error during read operation: {e}")
            raise

    def update(self, query, update_data, multiple=False):
        if query is not None and update_data is not None:
            try:
                if multiple:
                    result = self.collection.update_many(query, {'$set': update_data})
                else:
                    result = self.collection.update_one(query, {'$set': update_data})
                logging.info(f"Update operation successful. Modified count: {result.modified_count}")
                return result.modified_count
            except Exception as e:
                logging.error(f"Error during update operation: {e}")
                raise
        else:
            logging.warning("Update operation failed: Query or update_data is empty")
            raise Exception("Query or update_data is empty")

    def delete(self, query):
        if query is not None:
            try:
                result = self.collection.delete_many(query)
                logging.info(f"Delete operation successful. Deleted count: {result.deleted_count}")
                return result.deleted_count
            except Exception as e:
                logging.error(f"Error during delete operation: {e}")
                raise
        else:
            logging.warning("Delete operation failed: Query is empty")
            raise Exception("Query is empty")

    def search(self, criteria):
        try:
            results = list(self.collection.find(criteria))
            logging.info(f"Search operation successful. Found {len(results)} records.")
            return results
        except Exception as e:
            logging.error(f"Error during search operation: {e}")
            raise