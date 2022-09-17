import json
from os import path
from typing import Any


class Configuration:
	config_path: str = "src/Config/main.json"

	@staticmethod
	def save(key: str, value: Any, file_path: str = config_path) -> bool:
		saved: bool
		if path.exists(file_path):
			contents = json.load(open(file_path))
		else:
			contents: dict = {}
		contents[key] = value
		with open(file_path, "w") as json_file:
			json.dump(contents, json_file, indent=2)
			saved = True
		return saved

	@staticmethod
	def load(key: str, as_dict: bool = False, file_path: str = config_path) -> Any:
		value: Any = None
		if path.exists(file_path):
			contents = json.load(open(file_path))
			if key in contents:
				value = contents[key]
				if as_dict:
					value = {key: value}
		return value

	@staticmethod
	def delete(key: str, file_path: str = config_path) -> bool:
		deleted: bool
		if path.exists(file_path):
			contents = json.load(open(file_path))
			if key in contents:
				contents.pop(key)
				with open(file_path, "w") as json_file:
					json.dump(contents, json_file, indent=2)
					deleted = True
		return deleted
