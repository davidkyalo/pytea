from flask import _app_ctx_stack, _request_ctx_stack
from . import exc
from flask.app import setupmethod

def top_app_ctx(error=True, action=None):
	ctx = _app_ctx_stack.top
	if ctx is None and error:
		error = 'The application context not pushed.' \
				if error is True else error
		if action is not None:
			error = '{} {} requires the application '\
					'context.'.format(error, action)
		raise exc.AppContextError(error)
	return ctx

def top_request_ctx(error=True, action=None):
	ctx = _request_ctx_stack.top
	if ctx is None and error:
		error = 'The request context not pushed.' \
				if error is True else error
		if action is not None:
			error = '{} {} requires the request ' \
				'context. e.g within an HTTP request.'\
				.format(error, action)
		raise exc.RequestContextError(error)
	return ctx
