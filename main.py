import socket

from flask import Flask, make_response
from xf_auth.Auth import Auth

from src.Config.InitApp import init_config
from src.Model.User.User import User

Auth.set_user_origin(User)
Auth.set_user_keys(["email", "password"])
Auth.set_role_attribute("is_admin")

app = Flask(__name__)


@app.route("/")
def hello_world():
	return f"Hello world from: {socket.gethostname()}"


@app.route("/", defaults={"path": ""})
@app.route("/<path:path>", methods=["OPTIONS"])
def preflight(path):
	response = make_response()
	response.headers.add("Access-Control-Allow-Origin", "*")
	response.headers.add('Access-Control-Allow-Headers', "*")
	response.headers.add('Access-Control-Allow-Methods', "*")
	return response


app = init_config(app)

if __name__ == '__main__':
	app.run(host=app.host, port=app.port)
