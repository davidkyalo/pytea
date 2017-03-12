import re
import sys
import flask
import inspect
import flask_classy
from .flask_classy import FlaskView, route
from tea.flask import redirect
from .. import signals
from tea.collections import unique_list, stack
from . import mixins, exc
from textmate.config import views as views_config
from tea.importer import import_object
from tea.utils.six import with_metaclass
from tea.property import ThreadedCachedProperty


def dont_route(func):
	"""Decorator to indicate that view method is not to be routed."""
	setattr(func, '__norouting__', True)
	return func


class ViewMeta(type):
	def __new__(mcls, name, bases, body):
		body['_declared_attrs'] = list(body.keys())
		# Set __norouting__ so that it's not inherited.
		body.setdefault('__norouting__', [])
		# Set default abstract value
		body.setdefault('__abstract__', False)
		cls = super(ViewMeta, mcls).__new__(mcls, name, bases, body)
		cls._prepare_view()
		cls._set_norouting_method_names()
		return cls

	def __init__(cls, name, bases, body):
		delattr(cls, '_declared_attrs')
		if not cls.__abstract__:
			app = getattr(cls, 'app', None)
			if app is not None:
				print('App set in view {}. '
					'Auto registration of views will soon be depreciated.'
					.format(cls.__name__))
				# cls.register(app)

	def _is_declared_attr(cls, attr):
		return attr in cls._declared_attrs

	def _prepare_view(cls):
		cls._setup_view_renderer()
		cls._setup_view_repository()
		cls._setup_view_serializers()
		cls._setup_view_filters()

	def _set_norouting_method_names(cls):
		"""Set __norouting__ list of method names for the class"""
		norouting = cls.__norouting__
		# Add methods decorated with @dont_route
		for name in cls._declared_attrs:
			attr = getattr(cls, name, None)
			if inspect.isfunction(attr) and getattr(attr, '__norouting__', None):
				norouting.append(name)

		# Merge __norouting__ from bases.
		for base in cls.__bases__:
			if isinstance(base, ViewMeta):
				norouting.extend(base.__norouting__)
			else:
				# If base is not a view then add all it's methods.
				meths = inspect.getmembers(base, predicate=inspect.isfunction)
				norouting.extend([m[0] for m in meths if not hasattr(getattr(base, m[0]), '_rule_cache') ])

		cls.__norouting__ = unique_list(norouting)

	def _setup_view_renderer(cls):
		"""Setup the view's render."""
		if issubclass(cls, mixins.RendererMixin) and not cls.__abstract__:
			if not(cls.renderer and cls._is_declared_attr('renderer')):
				if cls.renderer_class:
					if inspect.isfunction(cls.renderer_class):
						cls.renderer = ThreadedCachedProperty(cls.renderer_class)
					else:
						cls.renderer = cls.renderer_class()

			cls._assert_is_set('renderer')

	def _setup_view_repository(cls):
		"""Setup view repository if view extends the RepositoryMixin."""
		if issubclass(cls, mixins.RepositoryMixin) and not cls.__abstract__:
			if cls.repository and inspect.isfunction(cls.repository):
				cls.repository = ThreadedCachedProperty(cls.repository)
			cls._assert_is_set('repository')

	def _setup_view_serializers(cls):
		"""Setup serializer instances"""
		if issubclass(cls, mixins.SerializerMixin) and not cls.__abstract__:

			#Setup the single entity serializer if not declared in view.
			if not(cls.entity_serializer and cls._is_declared_attr('entity_serializer')):
				if not cls._is_declared_attr('entity_serializer') and cls.serializer_class:
					if inspect.isfunction(cls.serializer_class):
						cls.entity_serializer = ThreadedCachedProperty(
										cls.serializer_class, kwargs=dict(many=False))
					else:
						cls.entity_serializer = cls.serializer_class(many=False)

			#Setup the serializer for entity collections if not declared in view.
			if not(cls.collection_serializer and cls._is_declared_attr('collection_serializer')):
				if not cls._is_declared_attr('collection_serializer') and cls.serializer_class:
					if inspect.isfunction(cls.serializer_class):
						cls.collection_serializer = ThreadedCachedProperty(
										cls.serializer_class, kwargs=dict(many=True))
					else:
						cls.collection_serializer = cls.serializer_class(many=True)

			cls._assert_is_set('entity_serializer')
			cls._assert_is_set('collection_serializer')

	def _setup_view_filters(cls):
		cls._setup_view_fieldset_filter()
		cls._setup_view_search_filter()
		cls._setup_view_ordering_filter()
		cls._setup_view_pagination_filter()

	def _setup_view_fieldset_filter(cls):
		"""Setup the view's fieldset_filter if view extends the FieldSetFilterMixin."""
		if issubclass(cls, mixins.FieldSetFilterMixin) and not cls.__abstract__:
			if not(cls.fieldset_filter and cls._is_declared_attr('fieldset_filter')):
				config = views_config.FIELD_SET_FILTER
				filter_class = cls.filter_class or config.get('default_class', None)
				if filter_class:
					if isinstance(filter_class, str):
						filter_class = import_object(filter_class)

					kwargs = stack()
					kwargs.fields = cls.filter_fields
					kwargs.default_operator = cls.default_filter_operator or config.get('default_operator', None)

					if inspect.isfunction(filter_class):
						cls.fieldset_filter = ThreadedCachedProperty(filter_class, kwargs=kwargs)
					else:
						cls.fieldset_filter = filter_class(**kwargs)

			cls._assert_is_set('fieldset_filter')

	def _setup_view_search_filter(cls):
		"""Setup the view's fieldset_filter if view extends the FieldSetFilterMixin."""
		if issubclass(cls, mixins.SearchMixin) and not cls.__abstract__:
			if not(cls.search_filter and cls._is_declared_attr('search_filter')):
				config = views_config.SEARCH
				search_class = cls.search_class or config.get('default_class', None)
				if search_class:
					if isinstance(search_class, str):
						search_class = import_object(search_class)

					kwargs = stack()
					kwargs.param = cls.search_param or config.get('param', None)
					kwargs.fields = cls.search_fields
					kwargs.default_operator = cls.default_search_operator or config.get('default_operator', None)

					if inspect.isfunction(search_class):
						cls.search_filter = ThreadedCachedProperty(search_class, kwargs=kwargs)
					else:
						cls.search_filter = search_class(**kwargs)

			cls._assert_is_set('search_filter')

	def _setup_view_ordering_filter(cls):
		"""Setup the view's ordering_filter for ordering if view extends the OrderingMixin."""
		if issubclass(cls, mixins.OrderingMixin) and not cls.__abstract__:
			if not(cls.ordering_filter and cls._is_declared_attr('ordering_filter')):
				config = views_config.ORDERING
				ordering_class = cls.ordering_class or config.get('default_class', None)
				if ordering_class:
					if isinstance(ordering_class, str):
						ordering_class = import_object(ordering_class)

					kwargs = stack()
					kwargs.fields = cls.ordering_fields
					kwargs.ordering = cls.ordering
					kwargs.param = config.get('param', None) \
						if cls.ordering_param is None else cls.ordering_param
					kwargs.default_ordering = config.get('default_ordering', None) \
						if cls.default_ordering is None else cls.default_ordering

					if inspect.isfunction(ordering_class):
						cls.ordering_filter = ThreadedCachedProperty(ordering_class, kwargs=kwargs)
					else:
						cls.ordering_filter = ordering_class(**kwargs)

			cls._assert_is_set('ordering_filter')

	def _setup_view_pagination_filter(cls):
		"""Setup the view's ordering_filter for ordering if view extends the OrderingMixin."""
		if issubclass(cls, mixins.PaginationMixin) and not cls.__abstract__:
			if not(cls.pagination_filter and cls._is_declared_attr('pagination_filter')):
				config = views_config.PAGINATION
				pagination_class = cls.pagination_class or config.get('default_class', None)
				if pagination_class:
					if isinstance(pagination_class, str):
						pagination_class = import_object(pagination_class)

					kwargs = stack()
					kwargs.page_size = cls.pagination_page_size or config.get('page_size', None)
					kwargs.page_param = cls.pagination_param or config.get('page_param', None)
					kwargs.max_page_size = cls.pagination_max_page_size or config.get('max_page_size', None)
					kwargs.page_size_param = cls.pagination_page_size_param or config.get('page_size_param', None)

					if inspect.isfunction(pagination_class):
						cls.pagination_filter = ThreadedCachedProperty(pagination_class, kwargs=kwargs)
					else:
						cls.pagination_filter = pagination_class(**kwargs)

			cls._assert_is_set('pagination_filter')

	def _assert_is_set(cls, attr, allow_none=False):
		"""Raise ViewSetupError if view attribute is not set or if it's None (unless allow_none is True)."""
		if not hasattr(cls, attr) or (not allow_none and getattr(cls, attr) is None):
			raise exc.ViewSetupError("Required attribute: {} is not set in view {}.".format(attr, cls.__name__))


class BaseView(FlaskView):

	@classmethod
	def build_rule(cls, *args, **kwargs):
		rule = super(BaseView, cls).build_rule(*args, **kwargs)
		return rule if rule.endswith('/') else rule+'/'


class View(with_metaclass(ViewMeta, BaseView, mixins.ViewMixin)):
	__abstract__ = True


class PageView(View, mixins.TemplateMixin):
	__abstract__ = True

x = PageView.__id__
print(x)

#################################
# HTTP Error Handlers
# ###############################
@signals.app_booted.connect
def _register_error_handlers(app, **kwargs):
	@app.errorhandler(400)
	def bad_request(error):
		print('*'*80)
		print('A 400 error:', error)
		print('*'*80)
		return 'This is a bad request', 400

	@app.errorhandler(404)
	def not_found(error):
		print('*'*80)
		print('A 404 error:', error)
		print('*'*80)
		return 'This page does not exist', 404
