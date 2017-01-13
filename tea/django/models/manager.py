from django.db.models import Manager as BaseManager
from .const import ANYTHING

class Manager(BaseManager):

	def __init__(self, *args, **kwargs):
		super(Manager, self).__init__(*args, **kwargs)
		self._polymorphic = kwargs.get('polymorphic', True)

	def new(self, **kwargs):
		return self.model(**kwargs)

	@property
	def _is_polymorphic(self):
		return self.model._meta.is_polymorphic

	@property
	def _polymorphic_on(self):
		return self.model._meta.polymorphic_on

	@property
	def _polymorphic_identity(self):
		return self.model._meta.polymorphic_identity

	def _model_is_morphable(self):
		return self._polymorphic_identity is not NOTHING and self._polymorphic_on

	def _morph_queryset(self, qset):
		if self._is_polymorphic and self._polymorphic and self._polymorphic_identity is not ANYTHING:
			flt = { self._polymorphic_on.name : self._polymorphic_identity }
			return qset.filter(**flt)
		else:
			return qset

	def _get_queryset(self):
		return super(Manager, self).get_queryset()

	def get_queryset(self):
		return self._morph_queryset(self._get_queryset())


