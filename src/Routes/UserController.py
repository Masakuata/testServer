import json

from flask import Blueprint, request, Response
from xf_auth.Auth import Auth

from src.Model.User.User import User
from src.Routes.HTTPStatus import OK, RESOURCE_CREATED

user_routes = Blueprint("user_routes", __name__)


@user_routes.post("/login")
@Auth.requires_payload({"email", "password"})
def login():
	user = User()
	user.email = request.json["email"]
	user.set_password(request.json["password"], True)
	result: tuple[int, str] = user.login()
	response = Response(status=result[0])
	if result[0] == OK:
		response = Response(
			json.dumps({"token": result[1]}),
			status=result[0],
			mimetype="application/json")
	return response


@user_routes.post("/users")
@Auth.requires_payload({"name", "email", "password"})
def register():
	user = User()
	user.build_from_json(request.json)
	status = user.register()
	response = Response(status=status)
	if status == RESOURCE_CREATED:
		response = Response(
			json.dumps(user.dump_dict()),
			status=status,
			mimetype="application/json")
	return response
