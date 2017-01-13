from .const import *
from tea.wrapper import val
from .manager import Manager
from .utils import meta_options
from django.db import models as base
from django.db.models import Field

# try:
# 	from polymorphic.models import PolymorphicModel as BaseModel
# 	from polymorphic.base import PolymorphicModelBase as BaseModelMeta
# except :
from django.db.models import Model as BaseModel
from django.db.models.base import ModelBase as BaseModelMeta


from django.utils import timezone
from django.core.exceptions import FieldDoesNotExist
from polymorphic.models import PolymorphicModel

meta_options( **{
	# 'timestamped' 		: (False, True),
	# 'created_at_field'	: ('created_at', True),
	# 'updated_at_field'	: ('updated_at', True),
	'is_polymorphic' 		: (False, True),
	'polymorphism_type'		: (None, True),
	'polymorphic_on' 		: (None, True),
	'polymorphic_identity'	: (NOT_PROVIDED, False)
})


class ModelBase(BaseModelMeta):

	def __new__(mcls, name, bases, attrs):
		cls = super(ModelBase, mcls).__new__(mcls, name, bases, attrs)
		return cls

	def _prepare(cls):
		meta = cls._meta
		# 1. Add a manager if model has none
		if not meta.managers:
			if cls._cls_has_field('objects'):
				raise ValueError(
					"Model %s must specify a custom Manager, because it has a "
					"field named 'objects'." % cls.__name__
				)
			manager = Manager()
			manager.auto_created = True
			cls.add_to_class('objects', manager)
		#-----

		# 2. Call parent _prepare
		super(ModelBase, cls)._prepare()

		# 3. Add registered meta options if not yet added.
		options = meta_options()
		for key in options.keys():
			if hasattr(meta, key):
				continue
			value, inherit = options[key]
			if inherit:
				for parent in reversed( cls.__bases__ ):
					if hasattr(parent, '_meta') and hasattr(parent._meta, key ):
						value = getattr(parent._meta, key)
						break

			value = val(value, model=cls)
			setattr(meta, key, value)

		# 5. Setup polymorphism
		is_polymorphic = False
		if meta.polymorphic_on is not None:
			fname = meta.polymorphic_on if isinstance(meta.polymorphic_on, str) else meta.polymorphic_on.name
			setattr(meta, 'polymorphic_on', cls._cls_get_field(fname, False))

			identity = meta.polymorphic_identity
			if identity is NOT_PROVIDED:
				if meta.proxy:
					identity = cls.__name__
				else:
					identity = ANYTHING
			elif meta.polymorphic_identity is NOTHING:
				identity = "" if meta.polymorphic_on.blank and meta.polymorphic_on.empty_strings_allowed else None

			setattr(meta, 'polymorphic_identity', identity)
			is_polymorphic = True

		setattr(meta, 'is_polymorphic', is_polymorphic)
		#-----
	#End

	def _cls_has_field(cls, field):
		name = field if isinstance(field, str) else field.name
		fields = cls._meta.fields # cls._meta.get_fields( include_parents = include_parents, include_hidden = include_hidden )
		return any(f.name == name for f in fields)

	def _cls_get_field(cls, field, silent=True):
		name = field if isinstance(field, str) else field.name
		fields = cls._meta.fields # cls._meta.get_fields()
		for f in fields:
			if f.name == name:
				return f
		if not silent:
			raise AttributeError('%s has no field named %r' % (cls.__name__, name))
		return None


class Model(base.Model, metaclass=ModelBase):

	class Meta:
		abstract = True

	def __init__(self, *args, **kwargs):
		if self._meta.is_polymorphic:
			field = self._meta.polymorphic_on
			fname = field.attname
			identity = self._meta.polymorphic_identity
			value = kwargs.get(fname, NOT_PROVIDED)
			if value is not NOT_PROVIDED and identity is not ANYTHING and identity != value:
				raise PolymorphicIdentityTypeError.create(value, fname, self.__class__)

			if value is NOT_PROVIDED:
				kwargs[fname] = field.get_default() if identity is ANYTHING else identity

		super(Model, self).__init__(*args, **kwargs)


	def save(self, *args, **kwargs):
		self._check_polymorphic_identity()
		return super(Model, self).save(*args, **kwargs)

	def _check_polymorphic_identity(self):
		if self._meta.is_polymorphic:
			field = self._meta.polymorphic_on
			fname = field.attname
			identity = self._meta.polymorphic_identity
			value = getattr(self, fname)
			if identity is not ANYTHING and identity != value:
				raise PolymorphicIdentityTypeError.create(value, fname, self.__class__)


class PolymorphicIdentityTypeError(TypeError):
	"""Invalid value assignment for polymorphic"""
	@classmethod
	def create(cls, value, field, model, *args, **kwargs):
		message = 'Invalid value "{0}" provided for field "{1}" in model "{2}".'
		message = message.format(value, field, model.__name__)
		return cls(message, *args, **kwargs)