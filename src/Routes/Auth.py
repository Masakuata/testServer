from datetime import datetime
from functools import update_wrapper

from cryptography.fernet import Fernet
from flask import Response, request, session

from src.Model.User.User import User
from src.Routes.HTTPStatus import UNAUTHORIZED, SESSION_EXPIRED, FORBIDDEN, NOT_ACCEPTABLE
from src.Util.Util import decode, encode, included


class Auth:
	secret_password: bytes = None

	@staticmethod
	def set_password():
		Auth.secret_password = Fernet.generate_key()

	@staticmethod
	def requires_token(operation):
		def verify_auth(*args, **kwargs):
			token = request.headers.get("Token")
			saved_token = None
			try:
				saved_token = session["token"]
				response = Response(status=UNAUTHORIZED)
				if token is not None and saved_token is not None and token == saved_token:
					session.modified = True
					response = operation(*args, **kwargs)
			except KeyError:
				response = Response(status=UNAUTHORIZED)
				if token is not None and saved_token is None:
					response = Response(status=SESSION_EXPIRED)
			return response

		return update_wrapper(verify_auth, operation)

	@staticmethod
	def requires_role(role: str):
		def decorator(operation):
			def verify_role(*args, **kwargs):
				token = request.headers.get("Token")
				response = Response(status=FORBIDDEN)
				if token is not None:
					values = Auth.decode_token(token)
					response = Response(status=FORBIDDEN)
					if str(values["is_owner"]) == str(role):
						response = operation(*args, **kwargs)
				return response

			return update_wrapper(verify_role, operation)

		return decorator

	@staticmethod
	def requires_payload(required_fields: set):
		def decorator(operation):
			def verify_payload(*args, **kwargs):
				if not included(required_fields, request.json):
					response = Response(status=NOT_ACCEPTABLE)
				else:
					response = operation(*args, **kwargs)
				return response

			return update_wrapper(verify_payload, operation)

		return decorator

	@staticmethod
	def generate_token(user: User) -> str:
		if Auth.secret_password is None:
			Auth.set_password()
		timestamp = datetime.now().strftime("%H:%M:%S")
		value: str = user.email + "/"
		value += user.password + "/"
		value += timestamp
		return encode(value, Auth.secret_password)

	@staticmethod
	def decode_token(token: str) -> dict:
		decoded_token = decode(token, Auth.secret_password)
		decoded_token = decoded_token.split("/")
		return {
			"email": decoded_token[0],
			"password": decoded_token[1]
		}
