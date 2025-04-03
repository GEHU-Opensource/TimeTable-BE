import os
from urllib.parse import quote_plus

from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, InvalidURI

load_dotenv()


class MongoDriver:
    def __init__(self):
        self.client = None
        self.db = None
        self.mongo_uri = None
        self._setup_connection()

    def _setup_connection(self):
        try:
            username = os.getenv("MONGO_USERNAME", "mongoUser")
            password = os.getenv("MONGO_PASSWORD", "mongo23")
            db_name = os.getenv("MONGO_DB_NAME", "timetable_mongo_db")
            # Use a template with placeholders if provided, otherwise default.
            uri_template = os.getenv(
                "MONGO_DB_URI_TEMPLATE",
                "mongodb+srv://{username}:{password}@cluster0.pzphh.mongodb.net/{dbname}?retryWrites=true&w=majority"
            )

            if not username or not password or not db_name or not uri_template:
                raise ValueError("MongoDB credentials or URI template are missing in environment variables")

            encoded_username = quote_plus(username)
            encoded_password = quote_plus(password)

            self.mongo_uri = uri_template.format(
                username=encoded_username,
                password=encoded_password,
                dbname=db_name
            )

            self.client = MongoClient(self.mongo_uri)
            self.db = self.client[db_name]

            self._test_connection()
        except (ConnectionFailure, InvalidURI) as e:
            raise ConnectionError(f"Failed to connect to MongoDB: {e}")
        except ValueError as ve:
            raise ve

    def _test_connection(self):
        try:
            self.client.admin.command("ping")
            print("MongoDB connection established successfully.")
        except Exception as e:
            raise ConnectionError(f"MongoDB connection failed: {e}")

    def get_collection(self, collection_name):
        """Return the specified MongoDB collection."""
        return self.db[collection_name]

    def delete_many(self, collection_name, query):
        """Delete all documents matching the query in the specified collection."""
        collection = self.get_collection(collection_name)
        result = collection.delete_many(query)
        return result.deleted_count

    def insert_one(self, collection_name, document):
        """Insert a single document into the specified collection."""
        collection = self.get_collection(collection_name)
        return collection.insert_one(document)

    def find(self, collection_name, query):
        """Find documents in the specified collection matching the query."""
        collection = self.get_collection(collection_name)

        return collection.find(query)

    def update_one(self, collection_name, query, update, array_filters=None):
        """Update a single document in the specified collection."""
        collection = self.get_collection(collection_name)
        if array_filters:
            return collection.update_one(query, update, array_filters=array_filters)
        return collection.update_one(query, update)

    def delete_one(self, collection_name, query):
        """Delete a single document in the specified collection."""
        collection = self.get_collection(collection_name)
        return collection.delete_one(query)

    def find_one(self, collection_name, query):
        """Find a single document in the specified collection matching the query."""
        collection = self.get_collection(collection_name)
        return collection.find_one(query)

    def list_collections(self):
        """List all collection names in the database."""
        return self.db.list_collection_names()

    def save_file(self, filename, file_data):
        file_id = self.fs.put(file_data, filename=filename, content_type="application/zip")
        return str(file_id)

    def get_file(self, file_id):
        return self.fs.get(file_id)

    def delete_file(self, file_id):
        self.fs.delete(file_id)
    def close(self):
        """Close the MongoDB client connection."""
        if self.client:
            self.client.close()
