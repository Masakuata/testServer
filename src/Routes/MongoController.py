import csv
import json
from io import StringIO
from threading import Thread

from bson import json_util
from flask import Blueprint, request, Response
from xfss.RemoteSession import RemoteSession

from src.Config.MongoHandler import MongoHandler
from src.Routes.HTTPStatus import RESOURCE_CREATED, OK, NO_CONTENT, BAD_REQUEST

mongo_routes = Blueprint("mongo_routes", __name__)


@mongo_routes.post("/storage/<collection_name>")
@RemoteSession.requires_token
def upload_data(collection_name: str):
	response = Response(status=BAD_REQUEST)
	file = request.files.get("data")
	if file is not None:
		mongo: MongoHandler = MongoHandler()
		mongo.set_database("randomStorage")
		mongo.set_collection(collection_name)

		objects = []
		stream = StringIO(file.stream.read().decode("UTF-8"), newline=None)
		reader = csv.reader(stream)
		headers = reader.__next__()

		count = 0

		for row in reader:
			aux_object = {}
			for index in range(0, len(headers)):
				aux_object[headers[index]] = row[index]
			objects.append(aux_object)

			if len(objects) == 100:
				current_objects = objects
				count += len(current_objects)
				Thread(target=mongo.insert_many, args=current_objects).start()
				objects = []

		del stream
		del headers

		if len(objects) != 0:
			count += len(objects)

			mongo.insert_many(objects)

			response = Response(
				json.dumps({"records_created": count}),
				status=RESOURCE_CREATED)

			del objects
			del current_objects
			del count
			del mongo

	return response


@mongo_routes.get("/storage/<collection_name>")
@RemoteSession.requires_token
def get_database(collection_name: str):
	mongo: MongoHandler = MongoHandler()
	mongo.set_database("randomStorage")
	mongo.set_collection(collection_name)
	results = mongo.find_all()
	response = Response(status=NO_CONTENT)
	if len(results) > 0:
		response = Response(
			json_util.dumps(results),
			status=OK,
			mimetype="application/json")

	del mongo
	del results

	return response


@mongo_routes.delete("/storage/<collection_name>")
@RemoteSession.requires_token
def delete_database(collection_name: str):
	response = Response(status=NO_CONTENT)
	mongo: MongoHandler = MongoHandler()
	mongo.set_database("randomStorage")
	mongo.set_collection(collection_name)
	if mongo.delete_collection(collection_name):
		response = Response(status=OK)

	del mongo

	return response
