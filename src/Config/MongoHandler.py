import os

from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database
from pymongo.server_api import ServerApi

from src.Config.Configuration import Configuration


class MongoHandler:
	def __init__(self):
		self.database: Database or None = None
		self.collection: Collection or None = None

		conn_string: str = Configuration.load("connection_string")
		conn_string = conn_string.replace("<password>", os.getenv("DB_PASSWORD"))

		self.client = MongoClient(conn_string, server_api=ServerApi("1"))

	def set_database(self, database: str):
		self.database = self.client[database]

	def set_collection(self, collection: str):
		if collection not in self.database.list_collection_names():
			self.database.create_collection(collection)
		self.collection = self.database.get_collection(collection)

	def find_all(self) -> list:
		results: list = []
		if self.collection is not None:
			results = list(self.collection.find({}, {"_id": False}))
		return results

	def find_one(self, filters: dict = {}) -> dict or None:
		record: dict or None = None
		if self.collection is not None:
			record = self.collection.find_one(filters, {"_id": False})
		return record

	def insert_one(self, object: dict = None) -> bool:
		inserted: bool = False
		if self.collection is not None and object is not None:
			result = self.collection.insert_one(object)
			inserted = result.inserted_id is not None
		return inserted

	def insert_many(self, objects: list = []) -> bool:
		inserted: bool = False
		if self.collection is not None and len(objects) != 0:
			results = self.collection.insert_many(objects)
			inserted = results.inserted_ids is not None and len(results.inserted_ids) != 0
		return inserted

	def count(self, filters: dict = {}) -> int:
		quantity: int = 0
		if self.collection is not None:
			quantity = self.collection.count_documents(filters)
		return quantity
