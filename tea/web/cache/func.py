import os

__all__ = ['realpath', 'joinpaths', 'mkdir', 'pathexists', 'delpath', 'iter_slices', 'rename_temp_file']

realpath = os.path.realpath

def joinpaths(base, *paths, real = True):
	path = os.path.join(base, *paths)
	return realpath(path) if real else path

def mkdir(path):
	if pathexists(path):
		return
	os.makedirs(path)

def pathexists(base, *paths):
	path = joinpaths(base, *paths)
	return os.path.exists(path)

def delpath(path):
    if pathexists(path):
        os.remove(path)

def rename_temp_file(file, type):
    temp_path = file.path
    file.type = type
    dest_path = file.path
    try:
        os.rename(temp_path, dest_path)
        return True
    except:
        # file.path = temp_path
        return False

def iter_slices(string, slice_length):
    """Iterate over slices of a string."""
    pos = 0
    while pos < len(string):
        yield string[pos:pos + slice_length]
        pos += slice_length
