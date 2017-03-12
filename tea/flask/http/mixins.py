from . import exc, renderers
from flask import render_template, request
from tea.flask import redirect
from tea.collections import stack
from ..request import input

class ViewMixin(object):

	@property
	def request(self):
		return request

	@property
	def input(self):
		print('*'*80)
		print('The input property is depreciated. Use the request object.')
		print('*'*80)
		return input

	def redirect(self, location, code=302, safe=False, Response=None):
		return redirect(location, code=code, safe=False, Response=Response)


class SerializerMixin(object):
	"""docstring for SerializerMixin"""

	serializer_class = None
	entity_serializer = None
	collection_serializer = None
	serializer_strict_mode = True
	return_serialization_errors = False
	serialization_error_class = exc.SerializationError
	deserialization_error_class = exc.ValidationError

	def _is_serializer_strict_mode(self, strict=None):
		return self.serializer_strict_mode if strict is None else strict

	def _is_return_serialization_errors(self, with_errors=None):
		return self.return_serialization_errors if with_errors is None else with_errors

	def _handle_serialization_error(self, original, results, strict=None, many=False, args=None, kwargs=None):
		if self._is_serializer_strict_mode(strict):
			raise self.serialization_error_class(results.errors)

	def _handle_deserialization_error(self, original, results, strict=None, many=False, args=None, kwargs=None):
		if self._is_serializer_strict_mode(strict):
			raise self.deserialization_error_class(results.errors)

	def _load_one(self, data, *args, strict=None, with_errors=None, **kwargs):
		results = self.entity_serializer.load(data, *args, **kwargs)
		if results.errors:
			self._handle_deserialization_error(data, results, strict=strict, many=False, args=args, kwargs=kwargs)
		return results if self._is_return_serialization_errors(with_errors) else results.data

	def _loads_one(self, json_data, *args, strict=None, with_errors=None, **kwargs):
		results = self.entity_serializer.loads(json_data, *args, **kwargs)
		if results.errors:
			self._handle_deserialization_error(json_data, results, strict=strict, many=False, args=args, kwargs=kwargs)
		return results if self._is_return_serialization_errors(with_errors) else results.data

	def _load_many(self, data, *args, strict=None, with_errors=None, **kwargs):
		results = self.collection_serializer.load(data, *args, **kwargs)
		if results.errors:
			self._handle_deserialization_error(
					data, results, strict=strict, many=True, args=args, kwargs=kwargs)
		return results if self._is_return_serialization_errors(with_errors) else results.data

	def _loads_many(self, json_data, *args, strict=None, with_errors=None, **kwargs):
		results = self.collection_serializer.loads(json_data, *args, **kwargs)
		if results.errors:
			self._handle_deserialization_error(
					json_data, results, strict=strict, many=True, args=args, kwargs=kwargs)
		return results if self._is_return_serialization_errors(with_errors) else results.data

	def _dump_one(self, entity, *args, strict=None, with_errors=None, **kwargs):
		results = self.entity_serializer.dump(entity, *args, **kwargs)
		if results.errors:
			self._handle_serialization_error(
					entity, results, strict=strict, many=False, args=args, kwargs=kwargs)
		return results if self._is_return_serialization_errors(with_errors) else results.data

	def _dumps_one(self, entity, *args, strict=None, with_errors=None, **kwargs):
		results = self.entity_serializer.dumps(entity, *args, **kwargs)
		if results.errors:
			self._handle_serialization_error(
					entity, results, strict=strict, many=False, args=args, kwargs=kwargs)
		return results if self._is_return_serialization_errors(with_errors) else results.data

	def _dump_many(self, entities, *args, strict=None, with_errors=None, **kwargs):
		results = self.collection_serializer.dump(entities, *args, **kwargs)
		if results.errors:
			self._handle_serialization_error(
					entities, results, strict=strict, many=True, args=args, kwargs=kwargs)
		return results if self._is_return_serialization_errors(with_errors) else results.data

	def _dumps_many(self, entities, *args, strict=None, with_errors=None, **kwargs):
		results = self.collection_serializer.dumps(entities, *args, **kwargs)
		if results.errors:
			self._handle_serialization_error(
					entities, results, strict=strict, many=True, args=args, kwargs=kwargs)
		return results if self._is_return_serialization_errors(with_errors) else results.data

	def _load(self, data, *args, many=False, **kwargs):
		if many:
			return self._load_many(data, *args, **kwargs)
		else:
			return self._load_one(data, *args, **kwargs)

	def _loads(self, json_data, *args, many=False, **kwargs):
		if many:
			return self._loads_many(json_data, *args, **kwargs)
		else:
			return self._loads_one(json_data, *args, **kwargs)

	def _dump(self, entities, *args, many=False, **kwargs):
		if many:
			return self._dump_many(entities, *args, **kwargs)
		else:
			return self._dump_one(entities, *args, **kwargs)

	def _dumps(self, entities, *args, many=False, **kwargs):
		if many:
			return self._dumps_many(entities, *args, **kwargs)
		else:
			return self._dumps_one(entities, *args, **kwargs)


class RepositoryMixin(object):
	"""docstring for RepositoryMixin"""

	repository = None

	@property
	def repo(self):
		return self.repository

	@property
	def model_class(self):
		return self.repo.model_class

	def get_query(self):
		return self.repo.query()


class RendererMixin(object):
	"""docstring for RestMixin"""
	renderer = None
	renderer_class = None
	response_data = None

	@property
	def r(self):
		return self.renderer

	def get_response_data(self, data):
		return data

	def _build_response_data(self, data):
		default = self.response_data
		if default:
			if not isinstance(default, dict):
				raise exc.InvalidValueError("View attribute response_data "
					"must be of type: None or dict. {} given in {}."
					.format(type(default), self.__class__.__name__))

			data.update(default)
		data = self.get_response_data(data)
		if not isinstance(data, dict):
			raise exc.InvalidValueError("View's get_response_data() "
				"must return a dict. {} given in {}."
				.format(type(default), self.__class__.__name__))
		return data

	def render(self, *args, **kwargs):
		kwargs = self._build_response_data(kwargs)
		return self.renderer.render(*args, **kwargs)



class TemplateMixin(RendererMixin):
	template_name = None
	renderer_class = renderers.TemplateRenderer

	def get_template_name(self, template_name = None):
		return self.template_name if template_name is None else template_name

	def render(self, template_name_or_list=None, **context):
		template_name = self.get_template_name(template_name_or_list)
		if not template_name:
			raise exc.TemplateNameError("Error rendering template. "
				"template_name not specified in view {0}."
				.format(self.__class__.__name__))
		return super(TemplateMixin, self).render(template_name, **context)


class OrderingMixin(object):
	ordering_filter = None
	ordering = None
	ordering_param = None
	ordering_class = None
	ordering_fields = '__all__'
	default_ordering = None

	def _apply_ordering_filter(self, query, params):
		return self.ordering_filter(query, params)


class PaginationMixin(object):
	pagination_filter = None
	pagination_class = None
	pagination_param = None
	pagination_page_size = None
	pagination_max_page_size = None
	pagination_page_size_param = 'page_size'

	def _apply_pagination_filter(self, query, params):
		return self.pagination_filter(query, params)

class FieldSetFilterMixin(object):
	fieldset_filter = None
	filter_class = None
	filter_fields = None
	default_filter_operator = None

	def _apply_fieldset_filter(self, query, params):
		fields = stack()
		for k in self.fieldset_filter.params:
			if k in params:
				fields[k] = params.get(k)

		if isinstance(self, SerializerMixin):
			fields = self._load(fields, partial=True)

		return self.fieldset_filter(query, fields, params)


class SearchMixin(object):
	search_filter = None
	search_class = None
	search_fields = None
	search_param = None
	default_search_operator = None

	def _apply_search_filter(self, query, params):
		return self.search_filter(query, params)


class QueryFiltersMixin(FieldSetFilterMixin, SearchMixin, OrderingMixin, PaginationMixin):
	"""docstring for QueryFiltersMixin"""

	def _apply_query_filters(self, query, params):
		query = self._apply_fieldset_filter(query, params)
		query = self._apply_search_filter(query, params)
		query = self._apply_ordering_filter(query, params)
		query = self._apply_pagination_filter(query, params)
		return query
