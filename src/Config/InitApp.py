from typing import Any

from flask import Flask
from flask_cors import CORS
from xf_auth.Auth import Auth
from xf_auth.RemoteSession import RemoteSession

from src.Config.RemoteConfig import RemoteConfig
from src.Model.User.User import User
from src.Routes.MongoController import mongo_routes
from src.Routes.UserController import user_routes


def init_config(app: Flask) -> Any:
	Auth.set_user_origin(User)
	Auth.set_user_keys(["email", "password"])
	Auth.set_role_attribute("is_admin")

	CORS(app, supports_credentials=True)

	app.register_blueprint(mongo_routes)
	app.register_blueprint(user_routes)

	config: dict = RemoteConfig.load_whole()

	app.config["SECRET_KEY"] = config["SECRET_KEY"]
	# app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(minutes=config["TLT"])
	app.host = config["HOST"]
	app.port = config["PORT"]

	RemoteSession.set_address(config["XF_SESSION_SERVER"])

	return app
