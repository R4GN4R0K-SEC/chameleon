__G__ = "(G)bd249ce4"

from postgres_conn import postgres_class
from json import JSONEncoder, dumps
from collections import Mapping
from logging import DEBUG, Handler, WARNING, getLogger
from sys import stdout

class ComplexEncoder(JSONEncoder):
	def default(self, obj):
		return "Something wrong, deleted.."

def serialize_object(_dict):
	if isinstance(_dict, Mapping):
		return dict((k, serialize_object(v)) for k, v in _dict.items())
	else:
		return repr(_dict)

class CustomHandler(Handler):
	def __init__(self,logs_type):
		self.logs_type = logs_type
		if logs_type == None:
			self.logs_type = "terminal"
		self.db = None
		if "db" in self.logs_type or "all" in self.logs_type:
			self.db = postgres_class()
		Handler.__init__(self)

	def emit(self, record):
		if "db" in self.logs_type or "all" in self.logs_type:
			self.db.insert_into_data_safe(record.msg[0],dumps(serialize_object(record.msg[1]),cls=ComplexEncoder))
		if "terminal" in self.logs_type or "all" in self.logs_type:
			print(record.msg)
		stdout.flush()