from flask import (
	Request as BaseRequest, session,
	request, request_started, current_app
)
from cached_property import cached_property
from tea.collections import stack
from werkzeug.local import LocalProxy
from . import signals

class Request(BaseRequest):

	@cached_property
	def previous(self):
		return PreviousRequest(**session.get_previous_request_data({}))

	def _get_flashable_data(self):
		data = {}
		for p in PreviousRequest.properties:
			data[p] = getattr(self, p)
		return data


class PreviousRequest(object):
	properties = [
		'method', 'url', 'base_url',
		'url_root', 'script_root', 'path'
	]

	def __init__(self, **kwargs):
		for k,v in kwargs.items():
			setattr(self,k,v)

	def __getattr__(self, key):
		if key in self.properties:
			return None
		raise AttributeError("Attribute {0} not in old request object.".format(key))



class Input(object):
	"""docstring for Input"""
	_args = None
	_form = None
	_old = None

	def __init__(self, args=None, form=None):
		self._args = args
		self._form = form

	@property
	def args(self):
		if self._args is None:
			self._args = {}
			for k,v in request.args.items():
				self._args[k] = v
		return self._args

	@property
	def form(self):
		if self._form is None:
			self._form = {}
			for k,v in request.form.items():
				self._form[k] = v
		return self._form

	@property
	def values(self):
		values = {}
		values.update(self.args)
		values.update(self.form)
		return values

	@property
	def old(self):
		if self._old is None:
			self._old = Input(*session.get_old_input(({}, {})))
		return self._old

	def get(self, key, default=None):
		if key in self.form:
			return self.form[key]
		if key in self.args:
			return self.args[key]
		return default

	def flash_only(self, *keys):
		form = {}
		for k,v in self.form.items():
			if k in keys:
				form[k] = v
		args = {}
		for k,v in self.args.items():
			if k in keys:
				args[k] = v
		session.flash_input((args, form))

	def flash_except(self, *keys):
		form = {}
		for k,v in self.form.items():
			if k not in keys:
				form[k] = v
		args = {}
		for k,v in self.args.items():
			if k not in keys:
				args[k] = v
		session.flash_input((args, form))

	def flash_all(self):
		session.flash_input((self.args, self.form))


input = LocalProxy(lambda: _get_current_input())

def _get_current_input():
	request.path
	if not hasattr(request, '__input_obj'):
		setattr(request, '__input_obj', Input())
	return getattr(request, '__input_obj')


@signals.app_booted.connect
def _register_input_template_global(app, **kwargs):
	app.add_template_global(input, 'input')
