from requests_cache.backends import sqlite
from .func import *
from tea.collections import stack
from .data import ResponseData
from datetime import datetime
# from .downloader import add_to_queue
CHUNK_SIZE = 10240





class FileSysCache(sqlite.DbCache):

    _files_dir_suffix = '-data'
    _cache_files_ext = '.cache'

    def __init__(self, cachedir = 'cache', dbname = 'db', extension='.sqlite', **kwargs):
        location = joinpaths(cachedir, dbname)

        self._cachedir = cachedir
        self._files_dir_name = dbname + self._files_dir_suffix
        self._cache_files_ext =  dbname + self._cache_files_ext
        self._temp_files_ext =  self._cache_files_ext + '.temp'
        self._files_dir = joinpaths(cachedir, self._files_dir_name)
        self._check_dirs()
        super(FileSysCache, self).__init__(location=location, fast_save=False, extension=extension, **kwargs)

        if '_content' in self._response_attrs:
            self._response_attrs.remove('_content')

    def _check_dirs(self):
        mkdir(self._files_dir)

    def save_response(self, key, response, lazy = False):
        self.set_cache_file(key, response)
        self.fetch_response_data(response, lazy)
        self.responses[key] = self.reduce_response(response), datetime.utcnow()

    def fetch_response_data(self, response, lazy = False):
        response.data.type = self._temp_files_ext
        if response._content is False:
            with open(response.data.path, 'wb') as fo:
                for chunk in response.iter_content(CHUNK_SIZE):
                    fo.write(chunk)
            # rename_temp_file(response.data, self._cache_files_ext)
        elif response._content != None:
            response.data.write(response.content, True)

        rename_temp_file(response.data, self._cache_files_ext)
        response._content = None


    def set_cache_file(self, key, response):
        self.build_cache_file(key, response.data)


    def build_cache_file(self, key, fileobj = None):
        if not fileobj:
            fileobj = ResponseData()
        fileobj.location = self._files_dir
        fileobj.basename = key
        fileobj.type = self._cache_files_ext
        return fileobj


    def get_response_and_time(self, key, default=(None, None)):
        try:
            if key not in self.responses:
                key = self.keys_map[key]
            response, timestamp = self.responses[key]

        except KeyError:
            return default
        fileobj = self.build_cache_file(key)
        if not fileobj.exists:
            self.delete(key)
            return default

        result = self.restore_response(response)
        self.set_cache_file(key, result)


        return result, timestamp

    def delete(self, key):
        super(FileSysCache, self).delete(key)
        fileobj = self.build_cache_file(key)
        fileobj.delete()



from requests_cache.backends import registry as backend_reg
backend_reg['filesys'] = FileSysCache
