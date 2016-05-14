
try:

	import requests, requests_cache	
	from requests.models import Response
	from .filesys import FileSysCache
	from .data import DataProperty, ResponseData

except ImportError:
	raise ImportError("Module tea.web.cache requires 'requests' and 'requests_cache' installed.")


def install_cache(cache_dir, expire_after = None, dbname = 'db', backend = 'filesys'):
    requests_cache.install_cache(cache_dir,
            backend = backend, expire_after=expire_after, dbname = dbname)
    response_cache_props()



def response_cache_props():
    Response.data = DataProperty()

