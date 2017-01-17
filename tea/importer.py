import importlib, re


def import_module(name, package=None):
	return importlib.import_module(name, package=package)

def import_object(name, package=None):
	path = str(name).split('.')
	# matches = re.match("^()(\.(?:[a-zA-Z_]+)(?:[0-9a-zA-Z_]+))$")
	module = import_module('.'.join(path[:-1]), package=package)
	return getattr(module, path[-1])