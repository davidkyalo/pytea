import logging as pylog
import datetime
import functools
from datetime import datetime as DTM
import time, json, os, traceback
from operator import itemgetter
from tea import disk
from tea.collections import stack
"""
    Timezone aware datetimes.

    Requires
    --------
    pytz
    tzlocal
"""

class Logger(object):
    """docstring for Logger"""
    path = None

    def __init__(self, app_name = 'app', global_path = '', contexts_path = None, time_watched = False,verbose = False):
        self.app_name = app_name
        self.global_path = global_path
        self.contexts_path = contexts_path if contexts_path else global_path
        self.contexts = stack()
        self.time_watched = time_watched
        self.time_stamp = DTM.now().strftime('%Y-%m-%d_%H-%M-%S')
        self.verbose = verbose
        self.add_context(app_name, global_path)
        self.add_context('timer', global_path)
        self.add_context('error_traceback', global_path)
        self.resetcontext()
        # self.echo_all = False
        # self.echo_stream = []

    def add_context(self, key, path = None):
        self.contexts[key] = path

    def context(self, key):
        self.set_current_context(key)
        return self

    def get_context_path(self, key):
        dirname = self.contexts.get(key, self.contexts_path)
        path = os.path.join(dirname, self.time_stamp)
        disk.mkdir(path)
        return os.path.join(path, key + '.log')

    def set_current_context(self, key):
        self.current_context = (key, self.get_context_path(key))

    def resetcontext(self):
        self.set_current_context(self.app_name)

    def write(self, msg):
        text = '{},\n'.format(msg)

        with open(self.current_context[1], 'a') as f:
            f.write(text)


    def log(self, *args, sep = '\n'):
        msg = self.makemsg(dumptojson, sep, *args)
        # if self.echo_all or self.current_context[0] in self.echo_stream:
        #     print(msg)
        self.write(msg)
        self.resetcontext()

    def traceback(self, *args, sep = '\n'):
        args += (traceback.format_exc(),)
        self.error_traceback.log(*args, sep = sep)

    def echo(self, *args, sep = '\n'):
        msg = self.makemsg(dumptojson, sep, *args)
        print(msg)
        self.write(msg)
        self.resetcontext()

    def makemsg(self, func, sep, *args):
        text = sep.join([func(arg) for arg in args])
        return text

    def output(self, context, echo = False):
        return self.context(context).echo if echo else self.context(context).log

    def __getattr__(self, key):
        self.set_current_context(key)
        return self

    def timeit(self, func):
        def wrapped_func(*args, **kwargs):
            t0 = time.time()
            st = timetostr(t0)
            result = func(*args, **kwargs)
            t1 = time.time()
            elapsed = t1 - t0
            msg = stack()
            msg.call_to = str(func)
            msg.start = st
            msg.finish = timetostr(t1)
            msg.elapsed = '{} secs'.format(elapsed)
            self.timer.log(msg)
            return result
        return wrapped_func

    def watch(self, context = None, loud = None, echo = False):
        if not loud:
            loud = self.verbose
        if not context:
            context = self.app_name

        def wrapper(func):
            def wrapped_func(*args, **kwargs):

                texts = 'START call-to : "{0}"'.format(func)
                if loud:
                    params = stack()
                    params['*args'] = args
                    params['**kwargs'] = kwargs
                    texts += '\n{}'.format(dumptojson(params))

                self.output(context, echo)(texts)
                t0 = time.time()
                result = func(*args, **kwargs)
                t1 = time.time()
                elapsed = t1 - t0
                texts = 'DONE call-to : "{0}", time : "{1} secs"'.format(func, elapsed)

                if loud:
                    texts += '\nReturned : {}'.format(dumptojson(result))

                self.output(context, echo)(texts, '</END>')
                return result
            return wrapped_func
        return wrapper


def argtojson(obj):
    try:
        text = json.dumps(obj)
    except:
        text = '{}'.format(obj)
    return text

def dumptojson(obj):
    if isinstance(obj, str):
        return obj

    try:
        text = json.dumps(obj, indent = 4)
    except:
        text = '{}'.format(obj)
    return text


def datetimetostr(dtm, f = '%Y-%m-%d %H:%M:%S'):
    return dtm.strftime(f)

def timetostr(tm, f = '%d %b %Y at %H:%M:%S'):
    return time.strftime(f)



def _format_args(*args, **kwargs):
    return ' '.join(['{}'.format(x) for x in args])
