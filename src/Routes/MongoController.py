import json

from flask import Blueprint, request, Response

from src.Config.MongoHandler import MongoHandler
from src.Routes.HTTPStatus import RESOURCE_CREATED, NOT_ACCEPTABLE

mongo_routes = Blueprint("mongo_routes", __name__)


@mongo_routes.post("/database/<data_name>")
def upload_data(data_name: str):
	response = Response(status=NOT_ACCEPTABLE)
	file_data = request.files["data"].stream
	dict_keys = file_data.readline().decode("utf-8").strip().split(",")
	objects = []
	for row in file_data:
		row_values = row.decode("utf-8").strip().split(",")
		aux_object = {}
		for index in range(0, len(dict_keys)):
			aux_object[dict_keys[index]] = row_values[index]
		objects.append(aux_object)
	if len(objects) != 0:
		mongo = MongoHandler()
		mongo.set_database("testingDB")
		mongo.set_collection(data_name)
		mongo.insert_many(objects)
		response = Response(
			json.dumps({"records_created": len(objects)}),
			status=RESOURCE_CREATED
		)
	return response


@mongo_routes.get("/database/<name>")
def get_database(id: str):
	return "database endpoint still not working"
