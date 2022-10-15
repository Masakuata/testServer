from typing import Any

from werkzeug.security import generate_password_hash, check_password_hash
from xf_auth.RemoteSession import RemoteSession

from src.Config.Configuration import Configuration
from src.Config.MongoHandler import MongoHandler
from src.Routes.HTTPStatus import BAD_REQUEST, OK, NOT_FOUND, RESOURCE_CREATED, CONFLICT, HTTPStatus


class User:
	def __init__(self):
		self.name: str or None = None
		self.email: str or None = None
		self.password: str or None = None
		self.is_admin: bool = False

		# Database connection
		self.db_connection: MongoHandler = MongoHandler()

		# Temporary connection to get session server info
		self.db_connection.set_database("configuration")
		self.db_connection.set_collection("directory")
		Configuration.static_values["XF_SESSION_SERVER_IP"] = self.db_connection.find_one().get("XF_SESSION_SERVER")

		# Users database connection
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

	def login(self) -> tuple[int, str] or tuple[int]:
		login_status = self.__login_against_db()
		response: tuple[int, str] or tuple[int] = (HTTPStatus(login_status).name,)

		if login_status == OK:
			xf_session = self.__create_remote_session()
			response = (xf_session,)
			if type(xf_session) == str:
				response = (login_status, xf_session)

		return response

	def __login_against_db(self) -> int:
		netherite_status: int = BAD_REQUEST
		if self.email is not None and self.password is not None:
			result: dict = self.db_connection.find_one({"email": self.email})
			if result is not None and self.check_password(result["password"], self.password):
				netherite_status = OK
				self.name = result["name"]
				self.password = result["password"]
				self.is_admin = result["is_admin"]
			else:
				netherite_status = NOT_FOUND
		return netherite_status

	def __create_remote_session(self) -> str or int:
		payload: dict = {
			"email": self.email,
			"password": self.password,
			"role": None
		}
		if self.is_admin:
			payload["role"] = "admin"

		response = RemoteSession.init_session(payload)
		del payload
		return_value: str or int = response[0]
		if response[0] == HTTPStatus.RESOURCE_CREATED.value:
			return_value = response[1]

		del response
		return return_value

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
