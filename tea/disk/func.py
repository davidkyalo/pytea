import os
import glob
from .file import File

realpath = os.path.realpath
abspath = os.path.abspath

_join = os.path.join

def pathexists(base, *paths):
    path = abspath(_join(base, *paths) if paths else base)
    return os.path.exists(path)


def checkpath(base, *paths, real=False, abs=True):
    path = joinpaths(base, *paths, real=real, abs=abs)
    return path if os.path.exists(path) else None


def joinpaths(base, *paths, real=False, abs=True):
    path = _join(base, *paths)
    func= realpath if real else abspath if abs else None
    return func(path) if func else path

join = joinpaths


def dirname(base, *paths):
    path = abspath(_join(base, *paths) if paths else base)
    return os.path.dirname(path)

def userpath(path):
    return os.path.expanduser(path)

def mkdir(path):
    if pathexists(path):
        return
    os.makedirs(path)

def getfiles(path, recursive = True):
    if not recursive:
        return findfiles('*.*', path)

    files = []
    for root, dirnames, filenames in os.walk(path):
        for filename in filenames:
            files.append(File(location = root, name = filename))
    return files

def refreshlogsdir(path):
    if not pathexists(path):
        return mkdir(path)
    pattern = realpath(_join(path, '*'))
    fpaths = glob.glob(pattern)
    for fpath in fpaths:
        os.remove(fpath)

def findfiles(pattern, path = '', type = None):
    cls = type if type else File
    pathname = realpath(_join(path, pattern))
    fpaths = glob.glob(pathname)
    return [cls(path = p) for p in fpaths]

def findfile(pattern, path = '', type = None):
    cls = type if type else File
    pathname = realpath(_join(path, pattern))
    fpaths = glob.glob(pathname)
    return cls(path = fpaths[0]) if len(fpaths) > 0 else None

def copyfile(path, dest, name = None):
    srcfile = File(path = path)
    bits = srcfile.binary
    destfile = File(path = path)
    destfile.location = dest
    if name:
        destfile.name = name
    destfile.write(bits, True)
    return destfile

def finddirs(self):
    pass

