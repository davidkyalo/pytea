from . import base

class Fineries(base.Base):
	"""docstring for Fineries"""

	def fire(self, hook, value, count_callbacks = False, feedback_handler = None, **kwargs):
		handler = self.get_feedback_handler(feedback_handler)
		callbacks = self.get_callbacks(hook)
		count = 0
		for callback, args in callbacks:
			data = self.build_callback_args(args, kwargs)
			value = handler( callback( value, **data ) )
			count += 1

		return (value, count) if count_callbacks else value