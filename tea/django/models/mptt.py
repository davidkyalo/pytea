from . import core
from mptt import models as base
from polymorphic_tree import models as polytree
from polymorphic.base import PolymorphicModelBase as PolymorphicMeta
from polymorphic.models import PolymorphicModel as PolymorphicBase
from polymorphic.manager import PolymorphicManager as BasePolymorphicManager
from mptt.models import MPTTModel, MPTTModelBase, TreeForeignKey
from polymorphic_tree.models import PolymorphicTreeForeignKey


"""Pure MPTT bases"""
class TreeManager(base.TreeManager, core.Manager):
	"""Manager"""
	pass

class TreeModelBase(base.MPTTModelBase, core.ModelBase):
	"""Metaclass"""
	pass

class MPTTModel(base.MPTTModel, core.Model, metaclass=TreeModelBase):
	"""Model"""
	objects = TreeManager()

	class Meta:
		abstract = True
"""END"""



"""Pure Polymorphic bases"""
class PolymorphicManager(BasePolymorphicManager, core.Manager):
	"""Manager"""
	pass

class PolymorphicModelBase(core.ModelBase, PolymorphicMeta):
	"""Metaclass"""
	pass

# class PolymorphicModel(PolymorphicBase, core.Model, metaclass=PolymorphicModelBase):
# 	"""Model"""
# 	objects = PolymorphicManager()

# 	class Meta:
# 		abstract = True

"""END"""



"""Polymorphic MPTT bases"""
class PolymorphicMPTTManager(polytree.PolymorphicMPTTModelManager, core.Manager):
	"""Manager"""
	pass

class PolymorphicMPTTModelBase(core.ModelBase, polytree.PolymorphicMPTTModelBase):
	"""Metaclass"""
	pass

# class PolymorphicMPTTModel(core.ModelBase, polytree.PolymorphicMPTTModel, metaclass=PolymorphicMPTTModelBase):
# 	"""Model"""
# 	# objects = PolymorphicMPTTManager()

# 	class Meta:
# 		abstract = True

"""END"""