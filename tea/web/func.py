import urllib.parse

def join_urls(base, url, allow_fragments = True):
    return urllib.parse.urljoin(base, url, allow_fragments = allow_fragments)

def join_url_paths(url, *fragments, endslash = True, endslash_file = False):
    url = url if url.endswith('/') else url + '/'
    for fragment in fragments:
        if not fragment.endswith('/'):
            fragment += '/'
        if fragment != '/':
            url += fragment

    if not endslash_file and '.' in fragments[-1]:
        endslash = False

    if not endslash and url.endswith('/'):
        url = url[:-1]
    return url
