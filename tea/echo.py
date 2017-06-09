from tea.decorators import classproperty
import curses
import re

class Echo:
	HEADER = '\033[95m'
	OKBLUE = '\033[94m'
	OKGREEN = '\033[92m'
	RED = '\033[31m'
	WARNING = '\033[93m'
	FAIL = '\033[91m'
	ENDC = '\033[0m'
	BOLD = '\033[1m'
	UNDERLINE = '\033[4m'

	COLS = None

	@classmethod
	def _set_cols(self, stdscr):
		self.COLS = curses.COLS

	@classproperty
	def cols(self):
		curses.wrapper(self._set_cols)
		return self.COLS

	@classmethod
	def hr(self, *args, hr='-', **kwargs):
		txt = self.format(*args, **kwargs)
		lt = len(txt)
		cols = self.cols
		ll = cols - lt
		if ll >= cols/10:
			left = right = hr*int(ll/2)
		else:
			sp = ' '*int(ll/2) if ll >= 4 else ''
			left = right = hr*cols
			left = '%s\n%s' % (left, sp)
			right = '%s\n%s' % (sp, right)

		rv = left+txt+right
		sp = cols - len(rv)
		if sp > 0:
			rv += hr*sp
		return rv

	@classmethod
	def format(self, *args, _=' ',  fargs=None, **fkwargs):
		text = _.join((str(a) for a in args))
		return text.format(*fargs, **fkwargs) if fargs or fkwargs else text

	@classmethod
	def header(self, *args, **kwargs):
		return self.HEADER + self.format(*args, **kwargs) + self.ENDC

	@classproperty
	def magenta(self):
		return self.header

	@classmethod
	def red(self, *args, **kwargs):
		return self.RED + self.format(*args, **kwargs) + self.ENDC

	@classmethod
	def blue(self, *args, **kwargs):
		return self.OKBLUE + self.format(*args, **kwargs) + self.ENDC

	@classmethod
	def green(self, *args, **kwargs):
		return self.OKGREEN + self.format(*args, **kwargs) + self.ENDC

	@classmethod
	def warn(self, *args, **kwargs):
		return self.WARNING + self.format(*args, **kwargs) + self.ENDC

	@classmethod
	def fail(self, *args, **kwargs):
		return self.FAIL + self.format(*args, **kwargs) + self.ENDC

	@classmethod
	def bold(self, *args, **kwargs):
		return self.BOLD + self.format(*args, **kwargs) + self.ENDC

	@classmethod
	def uline(self, *args, **kwargs):
		return self.UNDERLINE + self.format(*args, **kwargs) + self.ENDC

	@classmethod
	def echo(self, *args, f='', **kwargs):
		b4 = f
		if f and re.search(r'^(?:.*\,)?\s*(hr)\s*(?:\,.*)?$', f):
			txt = self.hr(*args, **kwargs)
			f = re.sub(r'^(.*\,)?\s*(hr)\s*(\,.*)?$', r'\1\3', f)
		else:
			txt = self.format(*args, **kwargs)

		for style in f.split(','):
			style = style.strip()
			if style.isdigit():
				txt = '\033[' + style + 'm' + txt + self.ENDC
			elif style:
				style = getattr(self, style)
				txt = style(txt)
		print(txt)

	def __call__(self, *args, **kwargs):
		return self.echo(*args, **kwargs)


echo = Echo()
