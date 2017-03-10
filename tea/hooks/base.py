from tea.collections import stack, Stack
from tea.wrapper import wrap

class Base(object):
	"""docstring for Base"""
	def __init__(self, feedback_handler = None, defult_level = None, default_level = None, \
			min_level = None, max_level = None, lock_callbacks = True):
		if not feedback_handler:
			feedback_handler = self.handle_feedback

		self.feedback_handler = feedback_handler
		self.lock_callbacks = lock_callbacks
		self.levels = stack()
		if defult_level is not None and default_level is None:
			default_level = defult_level

		self.levels.default = default_level
		self.levels.min = min_level
		self.levels.max = max_level

		self._init_hooks()

	def get_feedback_handler(self, handler = None):
		return handler if handler else self.feedback_handler

	def handle_feedback(self, feedback):
		return feedback

	def get_level(self, level):
		if level is None:
			return self.levels.default
		elif isinstance(level, str):
			return self.get_level( self.levels.get( level ) )
		elif self.levels.min != None and level < self.levels.min:
			return self.levels.min
		elif self.levels.max != None and level > self.levels.max:
			return self.levels.max
		else:
			return level

	def _init_hooks(self):
		self.hooks = stack()
		self.hooks.setdefault(Stack.ALL_ITEMS, wrap(self.new_hook))

	def new_hook(self):
		hook = stack()
		hook.setdefault(Stack.ALL_ITEMS, wrap(self.new_holder))
		return hook

	def new_holder(self):
		return []

	def islockable(self, lock):
		return self.lock_callbacks if lock is None else lock

	def get_hook(self, key):
		return self.hooks[key]

	def get_holder(self, key, level):
		hook = self.get_hook(key)
		return hook[level]

	def get_callbacks(self, key):
		hook = self.get_hook(key)
		callbacks = []

		for level, holder in sorted(hook.items()):
			callbacks.extend(holder)
		return callbacks

	def build_callback_args(self, args, data):
		if not args:
			return data
		kwargs = {}
		if args[0] is None:
			return kwargs

		for arg in args:
			kwargs[arg] = data[arg]

		return kwargs


	def bind_callback(self, hook, callback, level, args, lock, **kwargs):
		level = self.get_level(level)
		holder = self.get_holder(hook, level)
		holder.append( (callback, args) )
		return None if self.islockable(lock) else callback


	def __call__(self, hook, *args, level = None, lock = None, **kwargs):
		def wrapper(callback):
			return self.bind_callback(hook, callback, level, args, lock, **kwargs)
		return wrapper

	def bind(self, hook, callback, *args, level = None, lock = None, **kwargs):
		return self.bind_callback(hook, callback, level, args, lock, **kwargs)

	def prefire(self, hook, args, kwargs):
		pass

	def postfire(self, hook, args, kwargs):
		pass

	def fire_callbacks(self, callbacks, args, kwargs):
		pass

	def fire(self, hook, *args, **kwargs):
		pass
