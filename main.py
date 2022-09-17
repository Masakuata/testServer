from flask import Flask, make_response
from flask_cors import CORS

from src.Routes.MongoController import mongo_routes

app = Flask(__name__)
CORS(app, supports_credentials=True)

app.register_blueprint(mongo_routes)


@app.route("/")
def hello_world():
	return "Hello world"


@app.route("/", defaults={"path": ""})
@app.route("/<path:path>", methods=["OPTIONS"])
def preflight(path):
	response = make_response()
	response.headers.add("Access-Control-Allow-Origin", "*")
	response.headers.add('Access-Control-Allow-Headers', "*")
	response.headers.add('Access-Control-Allow-Methods', "*")
	return response


if __name__ == '__main__':
	app.run(host="0.0.0.0", port=42101)
