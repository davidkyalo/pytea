from .utils import order_dir
from sqlalchemy import asc, desc
from tea.decorators import cached_property
from tea.collections import stack, to_list

#########################################################
## Is this really thread safe??? Checkout the copy()s. ##
#########################################################

class Repository(object):
	"""Exposes an API for managing persistence operations for ORM-mapped objects.
	to the application layer.
	"""
	model_class = None
	proxy_query_methods = True
	context = {}

	def __init__(self, db, model_class=None, context=None):
		if self.__class__.context:
			self.context = self.__class__.context.copy()
		else:
			self.context = {}

		if context is not None:
			if not isinstance(context, dict):
				raise TypeError("Invalid context type. dict expected.")
			self.context.update(context)

		self.db = db

		if model_class is not None:
			self.model_class = model_class

		if isinstance(self.model_class, str):
			self.model_class = self.db.get_model(self.model_class)

	def new_query(self, *args, **kwargs):
		# if self.model_class not in args:
		# 	args = (self.model_class, ) + args
		return self.db.query(*(args or (self.model_class,)), **kwargs)

	def query(self, *args, **kwargs):
		return self.apply_context_filters(self.new_query(*args, **kwargs))

	def apply_context_filters(self, query):
		if not self.context:
			return query
		for k,v in self.context.items():
			query = query.filter(getattr(self.model_class, k) == v)
		return query

	def get(self, ident):
		return self.query().filter(*self._pk_criterion(ident)).first()

	def _pk_criterion(self, ident):
		if not isinstance(ident, (tuple, list)):
			ident = (ident,)
		criterion = []
		for col, val in zip(self.model_class.pk_columns(), ident):
			criterion.append(col == val)
		return criterion

	def default_create_data(self):
		return {}

	def get_create_data(self, data):
		default = self.default_create_data().copy()
		if data is not None:
			default.update(data)
		return default

	def create(self, data):
		model = self.create_model(self.get_create_data(data))
		return model

	def new_model(self, **data):
		return self.model_class(**data)

	def new(self, **data):
		return self.apply_context_data(self.new_model(**data))

	def create_model(self, data):
		model = self.new(**data)
		model.validate()
		return model

	def apply_context_data(self, model):
		if not self.context:
			return model
		for k,v in self.context.items():
			setattr(model, k, v)
		return model

	def default_update_data(self):
		return {}

	def get_update_data(self, data):
		default = self.default_update_data().copy()
		if data is not None:
			default.update(data)
		return default

	def update(self, model, data=None):
		model = self.update_model(model, self.get_update_data(data))
		return model

	def update_model(self, model, data):
		model.update(data)
		model.validate()
		return model

	def save(self, *models, before=None, after=None, identity=None):
		# raise Exception("Re implement this.")
		models = self.db.save(models, before=before, after=after, identity=identity)
		self.db.commit()
		return models

	def delete(self, *models):
		for model in models:
			self.db.delete(model)
		self.db.commit()
		return True

	def with_context(self, **context):
		repo = self.copy()
		repo.context.update(context)
		return repo

	def copy(self):
		return self.__class__(db=self.db, model_class=self.model_class, context=self.context)

	def __call__(self, **kwargs):
		return self.with_context(**kwargs)

	def __getattr__(self, key):
		attr = None
		if self.proxy_query_methods:
			query = self.query()
			attr = getattr(query, key, None)

		if attr is None:
			raise AttributeError('The attribute "{0}" is not an attribute of '
						'{1} nor is it available in of the query object for {2}.'
						.format(key, self.__class__, self.model_class))

		return attr

