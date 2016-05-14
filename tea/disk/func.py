import os
import glob
from .file import File

realpath = os.path.realpath

__join = os.path.join

def pathexists(base, *paths):
    path = realpath(__join(base, *paths))
    return os.path.exists(path)

def joinpaths(base, *paths, real = True):
    path = __join(base, *paths)
    return realpath(path) if real else path

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
    pattern = realpath(__join(path, '*'))
    fpaths = glob.glob(pattern)
    for fpath in fpaths:
        os.remove(fpath)



def findfiles(pattern, path = '', type = None):
    cls = type if type else File
    pathname = realpath(__join(path, pattern))
    fpaths = glob.glob(pathname)
    return [cls(path = p) for p in fpaths]

def findfile(pattern, path = '', type = None):
    cls = type if type else File
    pathname = realpath(__join(path, pattern))
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

