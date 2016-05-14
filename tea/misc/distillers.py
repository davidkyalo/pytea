
__all__ = [
	'sieve', 'collect', 'Funnel', 'Refinery', 'package'
]


class Filters(type):
	pass
		
class Filter(object, metaclass = Filters):
	"""docstring for Filter"""
	def __init__(self, func, *args, mapfunc = None, **kwargs):
		self.func = func
		self.mapfunc = mapfunc
		self.args = args
		self.kwargs = kwargs

	def getmapfunc(self, mapfunc = None):
		return self.mapfunc if self.mapfunc else mapfunc

	def map(self, item, mapfunc = None):
		if self.mapfunc:
			return self.mapfunc(item)
		elif mapfunc:
			return mapfunc(item)
		else:
			return item

	def apply(self, distiller, item, mapfunc = None):
		if isinstance(self.func, Distillers):
			result = distiller.nest(self.func, item, *self.args, **self.kwargs)
		else:
			mapped = self.map(item, mapfunc)
			func = self.func
			result = func(mapped, *self.args, distiller = distiller, **self.kwargs)
		return result


class sieve(Filter):
	pass

class collect(Filter):
	def __init__(self, func, packages, *args, keep = False, mapfunc = None, **kwargs):
		super(collect, self).__init__(func, *args, mapfunc = mapfunc, **kwargs)
		self.packages = packages if isinstance(packages, tuple) else (packages,)
		self.keep = keep
	
	def pack_item(self, item):
		for package in self.packages:
			package.pack(item)

	def apply(self, distiller, item, mapfunc = None):
		result = super(collect, self).apply(distiller, item, mapfunc = mapfunc)		
		if not result:
			return True

		self.pack_item(item)
		return True if self.keep else False


import collections



class Distillers(type):
	pass
		
		
class Distiller(object, metaclass = Distillers):

	"""docstring for Distiller"""

	def __init__(self, *units, mapfunc = None):
		self.units = units
		self.items = None
		self.mapfunc = mapfunc

	def __call__(self, item):
		return self.apply(item)
		

	def apply(self, item):
		for unit in self.units:
			if not unit.apply(self, item, self.mapfunc):
				return False
		return True

	def run(self, items, items_mapper = None, filter_mapper = list,):
		if items_mapper:
			self.mapfunc = items_mapper
		self.items = items

		filtered = filter(lambda item: self.apply(item), items)
		return filter_mapper(filtered)

	def nest(self, cls, item, *units, mapfunc = None):
		if not mapfunc:
			mapfunc = self.mapfunc
			
		instance = cls(*units, mapfunc = mapfunc)
		instance.items = self.items

		return instance.apply(item)



class Funnel(Distiller):
	"""docstring for Funnel"""
	pass



class Refinery(Distiller):
	"""docstring for Refinery"""
	pass


class package(list):
	def __init__(self, mapfunc = None, multipack = False):
		super(package, self).__init__()
		self._mapfunc = mapfunc
		self._multipack = multipack

	def pack(self, item):
		if self._mapfunc:
			item = self._mapfunc(item)

		if self._multipack:
			self.extend(item)
		else:
			self.append(item)

