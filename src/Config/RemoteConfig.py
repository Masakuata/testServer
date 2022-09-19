from typing import Any

from src.Config.MongoHandler import MongoHandler


class RemoteConfig:
	@staticmethod
	def save_remote(key: str, value: Any) -> bool:
		conn = MongoHandler()
		conn.set_database("configuration")
		db = conn.database
		if "mainServerConfig" not in db.list_collection_names():
			db.create_collection("mainServerConfig")
		collection = db.get_collection("mainServerConfig")
		if collection.count_documents({}) == 1:
			result = collection.update_one({}, {"$set": {key: value}}).acknowledged
		else:
			result = collection.insert_one({key: value}).acknowledged
		return result

	@staticmethod
	def load_remote(key: str) -> Any or None:
		conn = MongoHandler()
		conn.set_database("configuration")
		db = conn.database
		if "mainServerConfig" not in db.list_collection_names():
			db.create_collection("mainServerConfig")
		collection = db.get_collection("mainServerConfig")
		result = collection.find_one()
		value: Any = None
		if result is not None:
			if result.__contains__(key):
				value = result.get(key)
		return value

	@staticmethod
	def load_whole() -> dict or None:
		conn = MongoHandler()
		conn.set_database("configuration")
		db = conn.database
		if "mainServerConfig" not in db.list_collection_names():
			db.create_collection("mainServerConfig")
		collection = db.get_collection("mainServerConfig")
		return collection.find_one()
