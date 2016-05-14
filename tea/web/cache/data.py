from tea.disk import File
from .func import *

CHUNK_SIZE = 1024

class ResponseData(File):

    def __init__(self, *args, **kwargs):
        super(ResponseData, self).__init__(*args, **kwargs)


    @property
    def exists(self):
        return (self.path and pathexists(self.path))

    @property
    def content(self):
        # self.check_download()

        if self.exists:
            return self.read_contents('rb')
        return None

    @property
    def text(self):
        # self.check_download()
        if self.exists:
            return self.read_contents('r')
        return None

    @property
    def temp_path(self):
        if self.location != None and self.name:
            return os.path.join(self.location, self.name)
        elif self.location == None and self.name:
            return self.name
        else:
            return None
    # def is_ready(self):
    #     if in_queue(self.path):
    #         return False
    #     return True
    #
    # def check_download(self):
    #     if not self.is_ready():
    #         download(self.path)


    def delete(self):
        delpath(self.path)

    # def fetch_from(self, response, lazy):
    #     if lazy:
    #         self._lazy_loader = response
    #         self.status = 0
    #
    #
    # def _download(self, loader = None):
    #     if not loader:
    #         loader = self._lazy_loader
    #     if not loader or status == -1:
    #
    #     with open(self.path, 'wb') as fo:
    #         for chunk in iterator(chunk_size):
    #             fo.write(chunk)


from requests import Response

class DataProperty(object):
    propname = "_cache_data_obj_"

    def get_cache_file(self, instance, **kwargs):
        self.check_cache_file(instance, **kwargs)
        return getattr(instance, self.propname)

    def check_cache_file(self, instance, **kwargs):
        if not getattr(instance, self.propname, None):
            self.create_cache_file(instance, **kwargs)

    def create_cache_file(self, instance, **kwargs):
        cfile = ResponseData(**kwargs)
        cfile.response = instance
        setattr(instance, self.propname, cfile)

    def __get__(self, instance, cls):
        return self.get_cache_file(instance)

    def __set__(self, instance, value):
        if isinstance(value, ResponseData):
            # if not getattr(value, 'response', None):
            #     setattr(value, 'response', instance)
            setattr(instance, self.propname, value)
        else:
            raise TypeError('ResponseData required. {} given.'.format(type(value)))

# class FilesRegistry
