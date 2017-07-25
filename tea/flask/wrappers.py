from flask import Request as BaseRequest, Response as BaseResponse, jsonify
from . import signals
import six


class Request(BaseRequest):

	old = None
	old_json = None

	flashed_values = None
	flashed_json = None

	def flash(self, *keys, **kwargs):
		data = {}
		if keys:
			for key in keys:
				data[key] = self.values[key]
		if kwargs:
			data.update(kwargs)

		if self.flashed_values is None:
			self.flashed_values = data
		else:
			self.flashed_values.update(data)

	def flash_except(self, *keys):
		data = {}
		for key, value in self.values.items():
			if key not in keys:
				data[key] = value

		if self.flashed_values is None:
			self.flashed_values = data
		else:
			self.flashed_values.update(data)

	def flash_all(self):
		self.flash(*self.values.keys())

	def flash_json(self):
		self.flashed_json = self.get_json()

	def init_session(self, session):
		self._load_flashed_request(session)
		signals.session_ending.connect(self._save_flashed_request, session)

	def _save_flashed_request(self, session, app=None, **kwargs):
		if self.flashed_values is not None:
			session.flash('_old_request_values', self.flashed_values)
		if self.flashed_json is not None:
			session.flash('_old_request_json', self.flashed_json)

	def _load_flashed_request(self, session):
		self.old = session.pop('_old_request_values', {})
		self.old_json = session.pop('_old_request_json', None)




class Response(BaseResponse):
	
	def __init__(self, response=None, status=None, headers=None,
			mimetype=None, content_type=None, **kwargs):
		if self.should_be_json(response):
			rsp = self.morph_to_json(response, mimetype, content_type, headers)
			response, mimetype, content_type, headers = rsp
			
		super(Response, self).__init__(response, status, headers,
            mimetype=mimetype, content_type=content_type, **kwargs)
	
	def should_be_json(self, response):
		return not(response is None or not isinstance(response, dict))
	
	def morph_to_json(self, response, mimetype=None, content_type=None, headers=None):
		return jsonify(response), 'application/json', content_type, headers



class JSONResponse(Response):

	def should_be_json(self, response):
		return True
	