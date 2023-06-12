from threading import Thread
from typing import Any

import requests
from requests import Response
from werkzeug.security import generate_password_hash, check_password_hash
from xfss.RemoteSession import RemoteSession

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

		self.xg_login_result = None
		self.db_login_result = None
		self.session_login_result = None

	def set_password(self, password: str, clean: bool = False) -> None:
		if clean:
			self.password = password
		else:
			self.password = generate_password_hash(password)

	@staticmethod
	def check_password(hashed: str, clean: str) -> bool:
		return check_password_hash(hashed, clean)

	def login(self) -> tuple[int, str] or tuple[int]:
		xg_thread: Thread = Thread(target=self.__login_against_xg)
		session_thread: Thread = Thread(target=self.__create_remote_session)

		xg_thread.start()
		session_thread.start()

		xg_thread.join()
		session_thread.join()

		response: tuple[int, str] or tuple[int] = (HTTPStatus(self.xg_login_result).name,)

		if self.xg_login_result is not None and self.xg_login_result == OK:
			response = (self.session_login_result,)
			if type(self.session_login_result) == str:
				response = (self.xg_login_result, self.session_login_result)
			else:
				RemoteSession.close_session(self.session_login_result)
				del self.xg_login_result
				del self.session_login_result

		return response

	def __login_against_xg(self):
		self.xg_login_result: int = BAD_REQUEST
		if self.email is not None and self.password is not None:
			payload: dict = {"email": self.email, "password": self.password}
			url: str = Configuration.load("user_server_url") + "/user/login"
			response: Response = requests.post(url, json=payload)
			self.xg_login_result = HTTPStatus(response.status_code).value

	def __login_against_db(self):
		self.db_login_result: int = BAD_REQUEST
		if self.email is not None and self.password is not None:
			result: dict = self.db_connection.find_one({"email": self.email})
			if result is not None and self.check_password(result["password"], self.password):
				self.db_login_result = OK
				self.name = result["name"]
				self.password = result["password"]
				self.is_admin = result["is_admin"]
			else:
				self.db_login_result = NOT_FOUND

	def __create_remote_session(self):
		payload: dict = {
			"email": self.email,
			"password": self.password,
			"role": None
		}
		if self.is_admin:
			payload["role"] = "admin"

		response = RemoteSession.init_session(payload)
		del payload
		self.session_login_result = response["STATUS"]
		if response["STATUS"] == HTTPStatus.RESOURCE_CREATED.value:
			self.session_login_result = response["TOKEN"]

		del response

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
