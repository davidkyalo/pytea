from tea.enum import Enum

class JSendStatus:
	success = 'success'
	fail = 'fail'
	error = 'error'


class HttpStatus:
	OK = 200
	BAD_REQUEST = 400
	UNAUTHORIZED = 401
	FORBIDDEN = 403
	NOT_FOUND = 404
	METHOD_NOT_ALLOWED = 405
	NOT_ACCEPTABLE = 406
	REQUEST_TIMEOUT = 408
	SERVER_ERROR = 500;
	NOT_IMPLEMENTED = 501;
	BAD_GATEWAY = 502;
	SERVICE_UNAVAILABLE = 503;
