from tea import uzi, wrapper
from . import utils, core
from django.db import models
from django.db.models.base import ModelBase

def get_default_polymorphic_identity(model):
	return uzi.snake(model.__name__) if is_proxy_model(model) else None

def _get_polymorphic_identity_wapper():
	return wrapper.wrap( get_default_polymorphic_identity )

META_OPTIONS = {
	'polymorphic_on' 		: (None, True),
	'polymorphic_identity'	: (_get_polymorphic_identity_wapper(), False),
	'polymorphic_manager'	: (True, True),
	'polymorphic_strict' 	: (True, True)
}

core.meta_options(**META_OPTIONS)


def get_is_polymorphic_meta_func():
	def is_polymorphic(self):
		return isinstance(self.model, PolymorphicModelBase)

	return is_polymorphic

models.options.Options.is_polymorphic = get_is_polymorphic_meta_func()



def is_proxy_model(model):
	return getattr(model._meta, 'proxy', False)

def is_proxy_for(model):
	return getattr(model._meta, 'proxy_for_model', None)

def is_abstract_model(model):
	return getattr(model._meta, 'abstract', False)

def is_polymorphic(model):
	return model._meta.is_polymorphic()

def is_strict(model):
	return getattr(model._meta, 'polymorphic_strict', True)

def map_polymorphic_meta(model, key, default=None):
	if hasattr(model._meta, key):
		return getattr(model._meta, key)

	parent = is_proxy_for(model)
	if parent:
		value = map_polymorphic_meta(parent, key, default=default)
	else:
		value = default
	# if update:
	# 	setattr(model._meta, key, value)
	return value

def get_polymorphic_on(model, update=True, silent=False):
	polymorphic_on = map_polymorphic_meta(model, 'polymorphic_on')
	if not polymorphic_on and not is_abstract_model(model) and not silent:
		raise KeyError('Meta key "polymorphic_on" not set on model "{0}"', model.__name__)
	if update:
		set_polymorphic_on(model, polymorphic_on)

	return polymorphic_on

def get_polymorphic_identity(model, update=True):
	polymorphic_identity = map_polymorphic_meta(model, 'polymorphic_identity')
	if not polymorphic_identity:
		polymorphic_identity = get_default_polymorphic_identity(model)
	if update:
		set_polymorphic_identity(model, polymorphic_identity)

	return polymorphic_identity


def set_polymorphic_on(model, polymorphic_on):
	setattr(model._meta, 'polymorphic_on', polymorphic_on)

def set_polymorphic_identity(model, polymorphic_identity):
	setattr(model._meta, 'polymorphic_identity', polymorphic_identity)

def parse_new_model_kwargs(model, kwargs, update=False):
	polymorphic_on = get_polymorphic_on(model, update=update)
	polymorphic_identity = get_polymorphic_identity(model, update=update)
	if polymorphic_identity and polymorphic_on in kwargs and kwargs[polymorphic_on] != polymorphic_identity and is_strict(model):
		msg = 'Invalid polymorphic identity "{0}" for model "{1}". Should be "{2}"'
		raise ValueError(msg.format(kwargs[polymorphic_on], model.__name__, polymorphic_identity))

	if polymorphic_on not in kwargs:
		if polymorphic_identity:
			kwargs.update( { polymorphic_on : polymorphic_identity } )
	return kwargs



class Manager(core.Manager):

	def __init__(self, *args, **kwargs):
		super(Manager, self).__init__(*args, **kwargs)
		self._polymorphic_on = None
		self._polymorphic_identity = None
	# 	self._is_polymorphic_model = None

	# @property
	# def is_polymorphic_model(self):
	# 	return self._is_polymorphic_model


	@property
	def polymorphic_on(self):
		if not self._polymorphic_on:
			self.set_polymorphic_on(self.get_model_polymorphic_on())
		return self._polymorphic_on

	@property
	def polymorphic_identity(self):
		if not self._polymorphic_identity:
			self.set_polymorphic_identity( self.get_model_polymorphic_identity() )
		return self._polymorphic_identity

	# def polymorphic_identity(self, model = None):
	# 	model = model or self.model
	# 	return getattr(model._meta, 'proxy', False)

	# def _get_proxyed_model(self, model = None):
	# 	model = model or self.model
	# 	return getattr(model._meta, 'proxy_for_model', None)

	def get_model_polymorphic_on(self):
		return  #get_polymorphic_on(self.model, (not is_polymorphic(self.model)))

	def get_default_polymorphic_identity(self):
		return get_default_polymorphic_identity(self.model)

	def get_model_polymorphic_identity(self):
		return self.model._meta.polymorphic_on #get_polymorphic_identity(self.model, (not is_polymorphic(self.model)))

	def set_polymorphic_on(self, value):
		self._polymorphic_on = value

	def set_polymorphic_identity(self, value):
		self._polymorphic_identity = value

	def get_polymorphic_query_filters(self):
		return { self.polymorphic_on : self.polymorphic_identity } if self.polymorphic_identity else {}

	def morph_queryset(self, queryset):
		return queryset.filter(**self.get_polymorphic_query_filters())

	def get_queryset(self):
		return self.morph_queryset(super(Manager, self).get_queryset())

	def parse_create_kwargs(self, kwargs):
		parse_new_model_kwargs(self.model, kwargs)
		return kwargs

	def create(self, **kwargs):
		if not isinstance(self.model, PolymorphicModelBase):
			self.parse_create_kwargs(kwargs)
		return super(Manager, self).create(**kwargs)


class PolymorphicModelBase(core.ModelBase):

	def __new__(cls, name, bases, attrs):
		model = super(PolymorphicModelBase, cls).__new__(cls, name, bases, attrs)
		# get_polymorphic_on(model, True)
		# get_polymorphic_identity(model, True)
		return model

	def get_appropriate_manager(cls, manager):
		if manager.auto_created and getattr(cls._meta, 'polymorphic_manager', True):
			manager = Manager()
			manager.auto_created = True
			return manager
		return super(PolymorphicModelBase, self).get_appropriate_manager(manager)


class Model(core.Model, metaclass=PolymorphicModelBase):

	def __init__(self, *args, **kwargs):
		parse_new_model_kwargs(self.__class__, kwargs)
		return super(Model, self).__init__( *args, **kwargs)

	class Meta:
		abstract = True


