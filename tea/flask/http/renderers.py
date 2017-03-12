from flask import make_response, render_template
from .const import JSendStatus
from .serializers import JSendSchema
from textmate.utils.const import NOT_PROVIDED

class RendererMeta(type):
	pass

class Renderer(object, metaclass=RendererMeta):
	def __call__(self, *args, **kwargs):
		return self.render(*args, **kwargs)

	def render(self, *args, **kwargs):
		raise NotImplementedError(
				'Method render() in {}.'.format(self.__class__.__name__))


class TemplateRenderer(Renderer):
	"""docstring for TemplateRenderer"""
	def render(self, template_name_or_list, **context):
		return render_template(template_name_or_list, **context)


class JsonRenderer(Renderer):

	def render(self, *args, **kwargs):
		response = self.prepare(*args, **kwargs)
		return self.make_response(response)

	def prepare(self, *args, **kwargs):
		pass

	def make_response(self, *args):
		response = make_response(*args)
		response.mimetype = 'application/json'
		return response


class JSendRenderer(JsonRenderer):
	serializer = JSendSchema(partial=True)

	def prepare(self, status, data=None, meta=None, message=None, code=None):
		meta = {} if meta is None else meta
		response = dict(status = status, data = data, meta =meta)
		if message is not None:
			response['message'] = message
		if code is not None:
			response['code'] = code

		return self.serializer.dumps(response).data

	def render(self, *args, **kwargs):
		kwargs.setdefault('status', 'success')
		return super(JSendRenderer, self).render(*args, **kwargs)

	def success(self, data=None, meta=None, message=None, code=None):
		return self.render(status='success', data=data, meta=meta, message=message, code=code)

	def fail(self, data=None, meta=None, message=None, code=None):
		return self.render(status='fail', data=data, meta=meta, message=message, code=code)

	def error(self, message=None, code=None, data=None, meta=None):
		return self.render(status='error', data=data, meta=meta, message=message, code=code)

	def __getattr__(self, key):
		def _render(*args, **kwargs):
			kwargs.setdefault('status', key)
			return self.render(*args, **kwargs)
		return _render