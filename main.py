from flask import Flask, make_response

from src.Config.InitApp import init_config

app = Flask(__name__)


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


app = init_config(app)

if __name__ == '__main__':
	app.run(host=app.host, port=app.port)
