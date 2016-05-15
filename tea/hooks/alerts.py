from . import base

class Alerts(base.Base):
	"""docstring for Alerts"""

	def fire(self, hook, feedback_handler = None, **kwargs):
		handler = self.get_feedback_handler(feedback_handler)
		callbacks = self.get_callbacks(hook)
		count = 0
		for callback, args in callbacks:
			data = self.build_callback_args(args, kwargs)
			feedback = handler( callback( **data ) )
			count += 1
			if feedback == False:
				break
		return count