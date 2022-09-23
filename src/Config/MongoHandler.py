import os
from multiprocessing import Pool

from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database
from pymongo.server_api import ServerApi

from src.Config.Configuration import Configuration
from src.Util.Util import chunk_list


class MongoHandler:
	def __init__(self):
		self.database: Database = None
		self.collection: Collection = None

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

	@staticmethod
	def spawn_insert(objects: list) -> bool:
		handler = MongoHandler()
		handler.set_database("storage")
		handler.set_collection("multithread")
		return handler.insert_many(objects)

	@staticmethod
	def threaded_insert_many(database: str, collection: str, objects: list) -> bool:
		handler = MongoHandler()
		handler.set_database(database)
		handler.set_collection(collection)
		pool: Pool = Pool(processes=8)
		return all(
			pool.map(
				MongoHandler.spawn_insert,
				chunk_list(objects, 8)
			))

	def count(self, filters: dict = {}) -> int:
		quantity: int = 0
		if self.collection is not None:
			quantity = self.collection.count_documents(filters)
		return quantity

	def delete_one(self, filters: dict = {}) -> bool:
		deleted: bool = False
		if self.collection is not None:
			deleted = self.collection.delete_one(filters).deleted_count > 0
		return deleted

	def delete_many(self, filters: dict = {}) -> bool:
		deleted: bool = False
		if self.collection is not None:
			deleted = self.collection.delete_many(filters).deleted_count > 0
		return deleted

	def delete_collection(self, collection_name: str) -> bool:
		deleted: bool = False
		if self.database is not None and collection_name in self.database.list_collection_names():
			self.database.get_collection(collection_name).drop()
			deleted = collection_name not in self.database.list_collection_names()
		return deleted
