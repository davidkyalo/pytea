import flask
from urllib.parse import urlparse, urljoin
from flask import request, url_for
import warnings

def is_safe_url(target):
	error_msg = '{} in {} should be reimplemented.'\
		.format(is_safe_url.__name__, is_safe_url.__module__)
	warnings.warn(error_msg)
	real = urlparse(request.host_url)
	url = urlparse(urljoin(request.host_url, target))
	return url.scheme in ('http', 'https') and \
			real.netloc == url.netloc

def redirect(location, code=302, safe=False, Response=None):
	if safe and not is_safe_url(location):
		raise exc.UnSafeUrlError("Error redirecting to `{0}`.")
	return flask.redirect(location, code=code, Response=Response)
