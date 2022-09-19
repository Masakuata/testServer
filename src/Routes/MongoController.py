import csv
import json
from io import StringIO

from bson import json_util
from flask import Blueprint, request, Response

from src.Config.MongoHandler import MongoHandler
from src.Routes.HTTPStatus import RESOURCE_CREATED, NOT_ACCEPTABLE, OK, NO_CONTENT, BAD_REQUEST

mongo_routes = Blueprint("mongo_routes", __name__)


@mongo_routes.post("/storage/<collection_name>")
def upload_data(collection_name: str):
	response = Response(status=BAD_REQUEST)
	file = request.files.get("data")
	if file is not None:
		response = Response(status=NO_CONTENT)
		if file.content_length > 0:
			objects = []
			stream = StringIO(file.stream.read().decode("UTF-8"), newline=None)
			reader = csv.reader(stream)
			headers = reader.__next__()
			for row in reader:
				aux_object = {}
				for index in range(0, len(headers)):
					aux_object[headers[index]] = row[index]
				objects.append(aux_object)
			if len(objects) != 0:
				mongo: MongoHandler = MongoHandler()
				mongo.set_database("storage")
				mongo.set_collection(collection_name)
				mongo.insert_many(objects)
				response = Response(
					json.dumps({"records_created": len(objects)}),
					status=RESOURCE_CREATED)
	return response


@mongo_routes.get("/storage/<collection_name>")
def get_database(collection_name: str):
	mongo: MongoHandler = MongoHandler()
	mongo.set_database("storage")
	mongo.set_collection(collection_name)
	results = mongo.find_all()
	response = Response(status=NO_CONTENT)
	if len(results) > 0:
		response = Response(
			json_util.dumps(results),
			status=OK,
			mimetype="application/json")
	return response


@mongo_routes.delete("/storage/<collection_name>")
def delete_database(collection_name: str):
	response = Response(status=NO_CONTENT)
	mongo: MongoHandler = MongoHandler()
	mongo.set_database("storage")
	mongo.set_collection(collection_name)
	if mongo.delete_collection(collection_name):
		response = Response(status=OK)
	return response
