import inspect
from sqlservice.query import SQLQuery
from sqlalchemy import util, asc, desc, orm, Column as BaseColumn
from sqlalchemy.orm.base import _is_mapped_class
from tea.importer import import_object
from tea.exceptions import BadMethodCall
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy.orm.base import _generative
from . import utils
from sqlalchemy.sql.operators import Operators
import sqlalchemy
from warnings import warn

_query_class_map = {}

class QueryMeta(type):
	pass
	# def __new__(mcls, name, bases, attrs):
	# 	if name in _query_class_map:
	# 		raise NameError("Cannot redeclare query class {}".format(name))
	# 	cls = super(QueryMeta, mcls).__new__(mcls, name, bases, attrs)
	# 	_query_class_map[name] = cls
	# 	return cls

class BaseQuery(SQLQuery, metaclass=QueryMeta):
	pass

class _DynamicQuery(BaseQuery):
	pass

class Query(BaseQuery):

	def __new__(cls, *args, **kwargs):
		if cls is Query and len(args) > 0:
			clses = _get_enitity_queries(args[0])
			if len(clses) > 1:
				cls = _make_dynamic_query(clses)
			elif len(clses) == 1:
				cls = clses[0]
		return SQLQuery.__new__(cls)

	def order(self, order=asc):
		if self.model_classes:
			order = utils.getobj(order, sqlalchemy)
			criterion = [order(pk) for pk in utils.get_primary_key(self.model_classes[0])]
			return self.order_by(*criterion)
		return self

	# def find_by(self, , **kwargs):
	# 	return self.filter_by(**kwargs).all()

	def paginate(self, pagination, page=None):
		"""Return paginated query.

		Args:
			pagination (tuple|int): A ``tuple`` containing ``(per_page, page)``
				or an ``int`` value for ``per_page``.

		Returns:
			Query: New :class:`Query` instance with ``limit`` and ``offset``
				parameters applied.
		"""
		query = self
		per_page = None
		page = 1 if page is None else page

		if isinstance(pagination, (list, tuple)):
			per_page = pagination[0] if len(pagination) > 0 else per_page
			page = pagination[1] if len(pagination) > 1 else page
		else:
			per_page = pagination

		if per_page:
			query = query.limit(per_page)

		if page and page > 1 and per_page:
			query = query.offset((page - 1) * per_page)

		return query

	def search(self, *criterion, **kwargs):
		"""Return search query object.

		Args:
			*criterion (sqlaexpr, optional): SQLA expression to filter against.

		Keyword Args:
			per_page (int, optional): Number of results to return per page.
				Defaults to ``None`` (i.e. no limit).
			page (int, optional): Which page offset of results to return.
				Defaults to ``1``.
			order_by (sqlaexpr, optional): Order by expression. Defaults to
				``None``.

		Returns:
			Query: New :class:`Query` instance with criteria and parameters
				applied.
		"""
		order = kwargs.get('order')
		order_by = kwargs.get('order_by')
		page = kwargs.get('page')
		per_page = kwargs.get('per_page')
		limit = kwargs.get('limit')
		offset = kwargs.get('offset')

		query = self

		for criteria in pyd.flatten(criterion):
			if isinstance(criteria, dict):
				query = query.filter_by(**criteria)
			else:
				query = query.filter(criteria)

		if order_by is not None:
			if isinstance(order_by, (str, BaseColumn)):
				order = asc if order is None else utils.getobj(order, sqlalchemy)
				order_by = [order(order_by)]
			elif not isinstance(order_by, (list, tuple)):
				order_by = [order_by]
			query = query.order_by(*order_by)
		elif order is not None:
			query = query.order(utils.getobj(order, sqlalchemy))

		if per_page or page:
			query = query.paginate(per_page, page)
		elif limit or offset:
			if limit:
				query = query.limit(limit)
			if offset:
				query = query.offset(offset)

		return query




def _is_model(entity):
	return not isinstance(entity, util.string_types)\
		and not isinstance(entity, orm.Query)\
		and _is_mapped_class(entity)

def _get_query_class(entity, default=Query):
	if hasattr(entity, '_opts') and entity._opts.query_class:
		return entity._opts.query_class

	cls = getattr(entity, '__query_class__', None)

	if cls is not None:
		warn('Model option __query_class__ will soon be depreciated. '\
			'Use Meta option: query_class in model {}.'\
			.format(entity))

	if cls is None:
		cls = default
	elif isinstance(cls, util.string_types):
		if cls.startswith('..'):
			package = entity.__module__
		elif cls.startswith('.'):
			package = '.'.join(entity.__module__.split('.')[:-1])
		else:
			package = None
		cls = import_object(cls, package)
		setattr(entity, '__query_class__', cls)

	if inspect.isfunction(cls):
		cls = cls()
		setattr(entity, '__query_class__', cls)

	return cls

def _get_enitity_queries(entities):
	queries = []
	for entity in entities:
		if _is_model(entity):
			cls = _get_query_class(entity)
			if cls is not None and cls not in queries:
				queries.append(cls)
	return queries

def _make_dynamic_query(clses):
	name = ""
	bases = [_DynamicQuery]
	for cls in clses:
		if cls not in (Query, BaseQuery, _DynamicQuery) and cls not in bases:
			bases.append(cls)
			name += cls.__name__
	return QueryMeta(name, tuple(bases), {})
