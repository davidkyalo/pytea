
class Container(object):
	"""docstring for Container"""
	def __init__(self, arg):
		super(Container, self).__init__()
		self.arg = arg


class Extension(object):
	app = None

	def set_app(self, app):
		self.app = app
		self.init_app(app)

	def init_app(self, app):
		pass