from typing import Any

from werkzeug.security import generate_password_hash, check_password_hash

from src.Config.MongoHandler import MongoHandler
from src.Routes.HTTPStatus import BAD_REQUEST, OK, NOT_FOUND, RESOURCE_CREATED, CONFLICT


class User:
	def __init__(self):
		self.name: str or None = None
		self.email: str or None = None
		self.password: str or None = None
		self.is_admin: bool = False
		self.db_connection: MongoHandler = MongoHandler()
		self.db_connection.set_database("randomStore")
		self.db_connection.set_collection("users")

	def set_password(self, password: str, clean: bool = False) -> None:
		if clean:
			self.password = password
		else:
			self.password = generate_password_hash(password)

	@staticmethod
	def check_password(hashed: str, clean: str) -> bool:
		return check_password_hash(hashed, clean)

	def login(self) -> int:
		status: int = BAD_REQUEST
		if self.email is not None and self.password is not None:
			result: dict = self.db_connection.find_one({"email": self.email})
			if result is not None and self.check_password(result["password"], self.password):
				status = OK
				self.name = result["name"]
				self.password = result["password"]
				self.is_admin = result["is_admin"]
			else:
				status = NOT_FOUND
		return status

	def register(self) -> int:
		status: int = BAD_REQUEST
		if self.name is not None and self.email is not None and self.password is not None:
			if self.db_connection.count({"email": self.email}) == 0:
				if self.db_connection.insert_one(self.dump_dict(True)):
					status = RESOURCE_CREATED
			else:
				status = CONFLICT
		return status

	def dump_dict(self, include_password: bool = False) -> dict:
		aux_dict: dict = {
			"name": self.name,
			"email": self.email,
			"is_admin": self.is_admin
		}
		if include_password:
			aux_dict["password"] = self.password
		return aux_dict

	def build_from_json(self, values: dict) -> bool:
		loaded: bool = False
		for attribute in self.__dict__:
			if attribute in values:
				if attribute == "password":
					self.set_password(values[attribute])
				else:
					self.__setattr__(attribute, values[attribute])
					loaded = True
		return loaded

	@staticmethod
	def get_by_email(email: str) -> Any or None:
		result: Any = None
		if email is not None:
			db_connection = MongoHandler()
			db_connection.set_database("randomStore")
			db_connection.set_collection("users")
			result = db_connection.find_one({"email": email})
		return result
