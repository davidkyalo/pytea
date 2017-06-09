import sys
import os
import warnings
import importlib, re


def import_module(name, package=None):
	return importlib.import_module(name, package=package)

def import_object(name, package=None):
	# path = str(name).split('.')
	path = str(name).rsplit('.', 1)

	# module = import_module('.'.join(path[:-1]), package=package)
	module = import_module(path[0], package=package)
	return getattr(module, path[-1])



class ModuleMovedDeprecationWarning(DeprecationWarning):
	pass

warnings.simplefilter('always', ModuleMovedDeprecationWarning)


class PlaceHolderImporter(object):
	"""This importer redirects imports from this submodule to other locations.
	This makes it possible to continue using objects that have been moved. This
	way, it gives you a smooth time to make your transition.
	"""

	def __init__(self, module_choices, wrapper_module, new_location=None, old_location=None, warn=False):
		self.module_choices = module_choices
		self.wrapper_module = wrapper_module
		self.prefix = wrapper_module + '.'
		self.prefix_cutoff = wrapper_module.count('.') + 1
		self.new_location = new_location
		self.old_location = old_location or wrapper_module
		self.warn = warn

	def __eq__(self, other):
		return self.__class__.__module__ == other.__class__.__module__ and \
				self.__class__.__name__ == other.__class__.__name__ and \
				self.wrapper_module == other.wrapper_module and \
				self.module_choices == other.module_choices

	def __ne__(self, other):
		return not self.__eq__(other)

	def install(self):
		sys.meta_path[:] = [x for x in sys.meta_path if self != x] + [self]

	def find_module(self, fullname, path=None):
		if fullname.startswith(self.prefix):
			return self

	def load_module(self, fullname):
		if fullname in sys.modules:
			return sys.modules[fullname]

		modname = fullname.split('.', self.prefix_cutoff)[self.prefix_cutoff]

		if self.warn:
			warnings.warn(
				'Module {o} has been moved to new location {n}. '\
				'Importing {o}.{x} is deprecated, use {n}.{x} instead.'\
				.format(x=modname, o=self.old_location, n=self.new_location),
				ModuleMovedDeprecationWarning, stacklevel=2
			)

		for path in self.module_choices:
			realname = path % modname
			try:
				__import__(realname)
			except ImportError:
				exc_type, exc_value, tb = sys.exc_info()
				# since we only establish the entry in sys.modules at the
				# very this seems to be redundant, but if recursive imports
				# happen we will call into the move import a second time.
				# On the second invocation we still don't have an entry for
				# fullname in sys.modules, but we will end up with the same
				# fake module name and that import will succeed since this
				# one already has a temporary entry in the modules dict.
				# Since this one "succeeded" temporarily that second
				# invocation now will have created a fullname entry in
				# sys.modules which we have to kill.
				sys.modules.pop(fullname, None)

				# If it's an important traceback we reraise it, otherwise
				# we swallow it and try the next choice.  The skipped frame
				# is the one from __import__ above which we don't care about
				if self.is_important_traceback(realname, tb):
					reraise(exc_type, exc_value, tb.tb_next)
				continue
			module = sys.modules[fullname] = sys.modules[realname]
			if '.' not in modname:
				setattr(sys.modules[self.wrapper_module], modname, module)

			return module
		raise ImportError('No module named %s' % fullname)

	def is_important_traceback(self, important_module, tb):
		"""Walks a traceback's frames and checks if any of the frames
		originated in the given important module.  If that is the case then we
		were able to import the module itself but apparently something went
		wrong when the module was imported.  (Eg: import of an import failed).
		"""
		while tb is not None:
			if self.is_important_frame(important_module, tb):
				return True
			tb = tb.tb_next
		return False

	def is_important_frame(self, important_module, tb):
		"""Checks a single frame if it's important."""
		g = tb.tb_frame.f_globals
		if '__name__' not in g:
			return False

		module_name = g['__name__']

		# Python 2.7 Behavior.  Modules are cleaned up late so the
		# name shows up properly here.  Success!
		if module_name == important_module:
			return True

		# Some python versions will clean up modules so early that the
		# module name at that point is no longer set.  Try guessing from
		# the filename then.
		filename = os.path.abspath(tb.tb_frame.f_code.co_filename)
		test_string = os.path.sep + important_module.replace('.', os.path.sep)
		return test_string + '.py' in filename or \
			   test_string + os.path.sep + '__init__.py' in filename



def reraise(tp, value, tb=None):
	if value.__traceback__ is not tb:
		raise value.with_traceback(tb)
	raise value