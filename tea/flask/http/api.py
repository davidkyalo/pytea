from tea.flask import redirect
from textmate.exc import ValidationError
from .renderers import JSendRenderer
from .serializers import QueryOptionsSchema
from .view import route, ViewMeta, View
from tea.collections import stack
import inspect
from . import mixins, renderers


class ApiView(View, mixins.RendererMixin):
	__abstract__ = True


class RestApiView(ApiView, mixins.SerializerMixin, mixins.RepositoryMixin, mixins.QueryFiltersMixin):
	"""
	Base class for restful resource views.

	TODO: Come up with a workable authorization mechanism.
	"""
	__abstract__ = True
	renderer_class = JSendRenderer

	def response_meta(self):
		pass

	def index(self):
		query = self.get_query()
		query = self._apply_query_filters(query, self.request.args)

		print('*'*120)
		from pprint import pprint
		pprint(self.request.args, indent=2)
		print('*'*120)
		print(query)
		print('*'*120)

		models = query.all()

		meta = dict(
			total = self.repo.query().count(),
			request_data = self.request.args
		)

		if len(models) > 0:
			models = self._dump(models, many=True)

		return self.r.success(models, meta)

	@route('/<int:id>/')
	def get(self, id):
		model = self.repo.get(id)
		if model:
			model = self._dump(model)
			return self.r.success(model)

		return self.r.error("Resource not found.", 404)

	def post(self):
		raw = self.request.get_json()
		if not(isinstance(raw, dict) and 'data' in raw):
			return self.r.error("Invalid input.", 400)
		try:
			data = self._load(raw['data'])
			model = self.repo.create(data)
			self.repo.save(model)
		except ValidationError as error:
			return self.r.fail(error.messages, code=400)

		return self.r.success(self._dump(model))

	@route('/<int:id>/', methods=['PUT'])
	def put(self, id):
		model = self.repo.get(id)
		if not model:
			return self.r.error("Resource not found.", 404)

		raw = self.request.get_json()
		if not(isinstance(raw, dict) and 'data' in raw):
			return self.r.error("Invalid input.", 400)

		try:
			data = self._load(raw['data'], partial=True)
			self.repo.update(model, data)
			self.repo.save(model)
		except ValidationError as error:
			return self.r.fail(error.messages, code=400)

		return self.r.success(self._dump(model))


	#@route('/', methods=['DELETE'])
	@route('/<int:id>/', methods=['DELETE'])
	def delete(self, id):
		model = self.repo.get(id)
		if model:
			deleted = self.repo.delete(model)
			if not deleted:
				return self.r.fail("Invalid input.", code=400)
			return self.r.success(deleted)

		return self.r.error("Resource not found.", 404)


