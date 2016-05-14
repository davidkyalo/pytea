import os
from tea import uzi
from tea.collections import stack


class File(object):
    """docstring for File"""
    def __init__(self, path = None, location = None, name = None, basename = None, type = None, ext = None, local = True):
        self.location = location
        self.basename = basename
        self.type = type
        self.local = local
        if ext:
            self.ext = ext

        if path:
            self.path = path

        if name:
            self.name = name


    def __str__(self):
        return self.path

    def __iter__(self):
        with open(self.path, 'r') as f:
            for line in f:
                yield line

    @property
    def ext(self):
        return '.' + self.type if self.type else None

    @ext.setter
    def ext(self, value):
        if value[0] == '.':
            self.type = value[1:]
        else:
            self.type = value
        # self.type = value.replace('.', '')

    @property
    def name(self):
        if self.basename and self.ext:
            return self.basename + self.ext
        elif self.basename and not self.ext:
            return self.basename
        else:
            None

    @name.setter
    def name(self, value):
        self.basename, self.ext = os.path.splitext(value)

    @property
    def path(self):
        if self.location != None and self.name:
            return os.path.join(self.location, self.name)
        elif self.location == None and self.name:
            return self.name
        else:
            return None

    @path.setter
    def path(self, path):
        self.location = os.path.dirname(path)
        self.name = os.path.basename(path)

    def read_contents(self, mode):
        fo = open(self.path, mode)
        content = fo.read()
        fo.close()
        return content

    @property
    def content(self):
        return self.read_contents('r')

    @property
    def binary(self):
        return self.read_contents('rb')

    @property
    def exists(self):
        return os.path.exists(self.path)

    def append(self, content):
        fo = open(self.path, 'a')
        fo.write(content)
        fo.close()

    def write(self, content, binary = False):
        mode = 'wb' if binary else 'w'
        fo = open(self.path, mode)
        fo.write(content)
        fo.close()

    def print(self, content, mode = 'w'):
        print(content, file = open(self.path, mode))

    def writelines(self, lines, append = False):
        mode = 'a' if append else 'w'
        for l in lines:
            self.print(l, mode)
            mode = 'a'
        # mode = 'wb' if binary else 'w'
        # fo = open(self.path, mode)
        # fo.writelines(content)
        # fo.close()

    def minify(self):
        self.write(self.minified)

    @property
    def minified(self):
        return uzi.minify(self.content)

    def __str__(self):
        rep = '"file_object": "{0}", "path" : "{1}"'.format(self.__class__.__name__, self.path)
        return '{' + rep + '}'

    def __repr__(self):
        return self.__str__()

class TextFile(File):
    """docstring for TextFile"""
    def __init__(self, *args, type = 'txt', **kwargs):
        super(TextFile, self).__init__(*args, type = type, **kwargs)
