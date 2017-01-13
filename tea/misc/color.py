from tea import uzi

def hex_to_rgb(hx):
	hx = real_hex(hx)
	lv = len(hx)
	return tuple( int(hx[i:i + lv // 3], 16) for i in range(0, lv, lv // 3) )


def rgb_to_hex(rgb):
	return '#%02x%02x%02x' % rgb

def real_hex(value):
	value = value.lstrip('#')
	if len(value) == 3:
		value = ''.join([v*2 for v in value])
	return value


def is_valid_hex_str(value):
	if not isinstance(value, str):
		return False

	try:
		int(value.lstrip('#'), 16)
		return True
	except ValueError as e:
		return False

def parse_rgba_str(value):
	orig = value
	value = uzi.compact(value, all_spaces=True)

	if value.startswith('rgb'):
		value = value[3:]
	elif value.startswith('rgba'):
		value = value[4:]

	value = value.lstrip('(').rstrip(')')
	rgba = filter(lambda v: v.isdigit(), )

	rgba = []
	for v in value.split(','):
		if not v.isdigit():
			raise ValueError('Invalid RGBA string %s' % orig)
		rgba.append(int())

	if len(rgba) < 3:
		raise ValueError('Invalid RGBA string %s' % orig)


	value.lstrip()
	if not isinstance(value, str):
		return False
	# if value.starts

class Color(object):
	def __init__(self, *args, hexit=None, opacity=1, name=''):
		self._r = 0
		self._g = 0
		self._b = 0
		self._a = opacity
		self.name = name

		if len(args) == 1 and is_valid_hex_str(args[0]):
			hexit = args[0]

		if hexit is not None:
			self._r, self._g, self._b = hex_to_rgb(hexit)
		else:
			attrs = ('_r', '_g', '_b', '_a')
			i = 0
			for arg in args:
				setattr(self, attrs[i], arg)
				i +=1

		if self._a > 1 or self._a < 0:
			raise ValueError("Color opacity should be a value between 0 and 1. {0} given".format(self._a))

	@property
	def r(self):
		return self._r

	@property
	def g(self):
		return self._g

	@property
	def b(self):
		return self._b

	@property
	def a(self):
		return self._a

	@property
	def opacity(self):
		return self._a

	@property
	def rgb(self):
		return (self._r, self._g, self._b)

	@property
	def rgba(self):
		return (self._r, self._g, self._b, self._a)

	@property
	def hex(self):
		return rgb_to_hex(self.rgb)

	def __eq__(self, other):
		if isinstance(other, tuple):
			other = Color(*other)
		elif is_valid_hex_str(other):
			other = Color(hexit=other)

		if isinstance(other, Color):
			return self.rgba == other.rgba

		return NotImplemented

	def __hash__(self):
		return hash(self.rgba)

	def __str__(self):
		return 'rgba(%s,%s,%s,%s)' % self.rgba

	def __repr__(self):
		return '<%s %s> %s' % (self.__class__.__name__, self.name, self)


class Palette(object):
	pass

