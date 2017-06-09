import datetime, time, re
from pytz import timezone
from dateutil import tz

try:
	import arrow
except ImportError:
	arrow = None

if arrow:
	from arrow.util import is_timestamp, isstr


home_timezone = 'Africa/Nairobi'

def localized(zone_name, dtm = None):
	if not dtm:
		dtm = datetime.datetime.now()

	zone = timezone(zone_name)
	return zone.localize(dtm)


def home_time(dtm = None):
	athome = localized(home_timezone, dtm)
	return athome

def time_as_home(dtm):
	return time_as_zone(home_timezone, dtm)


def time_as_zone(zone_name, dtm = None):
	if zone_name == home_timezone:
		return home_time(dtm)

	if not dtm:
		dtm = home_time()

	return dtm.astimezone(timezone(zone_name))


def str_datetime(f = '%c', ts = None):
    if not ts:
        ts = time.time()
    norm_format = '%Y-%m-%d %H:%M:%S'
    return datetime.datetime.fromtimestamp(ts).strftime(f)


def int_time():
    return int(time.time())


def timetostr(dtm, f = None):
	if not dtm:
		return ' '
	if not f:
		f = '%H:%M:%S'
	return dtm.strftime(f)


def datetostr(dtm, f = None):
	if not dtm:
		return ' '
	if not f:
		f = '%d, %b %Y'
	return dtm.strftime(f)


def pretty_datetimetostr(dtm, f = None):
	if not dtm:
		return ' '
	if not f:
		f = '%d %a, %b %Y at %H:%M:%S'
	return dtm.strftime(f)


def ordinal(n):
	m100 = n % 100
	m10 = n % 10
	small = {1:'st', 2:'nd', 3:'rd'}
	return 'th' if 4 <= m100 <= 20 else small.get(m10, 'th')

ORDINAL_REGEX = re.compile(r'\{th\}')

def strftime(dtm, f, *args, **kwargs):
	# return dtm.strftime(f).replace('{th}', ordinal(dtm.day))
	th = ordinal(dtm.day) if isinstance(dtm, (datetime.datetime, datetime.date)) else ''
	return dtm.strftime(f).format(*args, th=th, **kwargs)


def happenedon(dtm, iconed = False, icon_cls = None):
	if not dtm:
		return ' '
	sep = ' - '
	icon = ''
	if iconed:
		icon_cls = 'fa fa-clock-o' if not icon_cls else icon_cls
		icon = ' <i class="{}"></i> '.format(icon_cls)
		sep = ', ' + icon


	now = datetime.datetime.now()
	delta = now - dtm
	f = '%b %d{th}, %Y'
	tf = '%H:%M'

	if delta_hrs(delta) < 1:
		f = icon + tf + ':%S'
	elif delta.days == 0 or delta_hrs(delta) <= 21: # delta.total_seconds() <= (60*60*21):
		f = icon + tf
	elif delta.days <= 6:
		f = 'Last %a'+ sep + tf
	elif now.month == dtm.month and delta.days <= 14:
		f = 'On %a {th}'+ sep + tf
	elif now.year == dtm.year or delta.days < 300:
		f = '%b {th}'+ sep + tf

	return strftime(dtm, f)


def delta_hrs(delta):
	secs = delta.total_seconds()
	return secs / (3600)


def deltatoweeks(self):
	pass


def datetimetostr(dtm, f = None):
	if not dtm:
		return ' '
	if not f:
		f = '%Y-%m-%d %H:%M:%S'
	return dtm.strftime(f)


_localtz_func = tz.tzlocal

def _to_localtz_func(value):
	if callable(value):
		return value
	def localtz():
		return localtz.value
	localtz.value = value
	return localtz


def localtz(*func):
	global _localtz_func
	if func:
		_localtz_func = _to_localtz_func(func[0])
		return _localtz_func
	return _localtz_func()

def systz():
	tz.tzlocal()


class Carbon(arrow.Arrow if arrow else object):
	def __init__(self, year, month, day, hour=0, minute=0, second=0, microsecond=0,
				tzinfo=None):
		# if tzinfo is None: tzinfo = localtz()
		super(Carbon, self).__init__(year, month, day, hour, minute, second,
			microsecond, tzinfo)


class Factory(arrow.ArrowFactory if arrow else object):

	def get(self, *args, **kwargs):
		''' Returns an :class:`Arrow <arrow.arrow.Arrow>` object based on flexible inputs.

		Usage::

			>>> import arrow

		**No inputs** to get current UTC time::

			>>> arrow.get()
			<Arrow [2013-05-08T05:51:43.316458+00:00]>

		**None** to also get current UTC time::

			>>> arrow.get(None)
			<Arrow [2013-05-08T05:51:43.316458+00:00]>

		**One** :class:`Arrow <arrow.arrow.Arrow>` object, to get a copy.

			>>> arw = arrow.utcnow()
			>>> arrow.get(arw)
			<Arrow [2013-10-23T15:21:54.354846+00:00]>

		**One** ``str``, ``float``, or ``int``, convertible to a floating-point timestamp, to get that timestamp in UTC::

			>>> arrow.get(1367992474.293378)
			<Arrow [2013-05-08T05:54:34.293378+00:00]>

			>>> arrow.get(1367992474)
			<Arrow [2013-05-08T05:54:34+00:00]>

			>>> arrow.get('1367992474.293378')
			<Arrow [2013-05-08T05:54:34.293378+00:00]>

			>>> arrow.get('1367992474')
			<Arrow [2013-05-08T05:54:34+0struct_time0:00]>

		**One** ISO-8601-formatted ``str``, to parse it::

			>>> arrow.get('2013-09-29T01:26:43.830580')
			<Arrow [2013-09-29T01:26:43.830580+00:00]>

		**One** ``tzinfo``, to get the current time in that timezone::

			>>> arrow.get(tz.tzlocal())
			<Arrow [2013-05-07T22:57:28.484717-07:00]>

		**One** naive ``datetime``, to get that datetime in UTC::

			>>> arrow.get(datetime(2013, 5, 5))
			<Arrow [2013-05-05T00:00:00+00:00]>

		**One** aware ``datetime``, to get that datetime::

			>>> arrow.get(datetime(2013, 5, 5, tzinfo=tz.tzlocal()))
			<Arrow [2013-05-05T00:00:00-07:00]>

		**One** naive ``date``, to get that date in UTC::

			>>> arrow.get(date(2013, 5, 5))
			<Arrow [2013-05-05T00:00:00+00:00]>

		**Two** arguments, a naive or aware ``datetime``, and a timezone expression (as above)::

			>>> arrow.get(datetime(2013, 5, 5), 'US/Pacific')
			<Arrow [2013-05-05T00:00:00-07:00]>

		**Two** arguments, a naive ``date``, and a timezone expression (as above)::

			>>> arrow.get(date(2013, 5, 5), 'US/Pacific')
			<Arrow [2013-05-05T00:00:00-07:00]>

		**Two** arguments, both ``str``, to parse the first according to the format of the second::

			>>> arrow.get('2013-05-05 12:30:45', 'YYYY-MM-DD HH:mm:ss')
			<Arrow [2013-05-05T12:30:45+00:00]>

		**Two** arguments, first a ``str`` to parse and second a ``list`` of formats to try::

			>>> arrow.get('2013-05-05 12:30:45', ['MM/DD/YYYY', 'YYYY-MM-DD HH:mm:ss'])
			<Arrow [2013-05-05T12:30:45+00:00]>

		**Three or more** arguments, as for the constructor of a ``datetime``::

			>>> arrow.get(2013, 5, 5, 12, 30, 45)
			<Arrow [2013-05-05T12:30:45+00:00]>

		**One** time.struct time::
			>>> arrow.get(gmtime(0))
			<Arrow [1970-01-01T00:00:00+00:00]>

		'''
		return super(Factory, self).get(*args, **kwargs)
        # arg_count = len(args)
        # locale = kwargs.get('locale', 'en_us')
        # tzinfo = kwargs.get('tzinfo', None)
		# local_tzinfo = localtz()

        # # () -> now, @ utc.
        # if arg_count == 0:
        #     return self.type.now(tzinfo)

        # if arg_count == 1:
        #     arg = args[0]

        #     # (None) -> now, @ utc.
        #     if arg is None:
        #         return self.type.now()

        #     # try (int, float, str(int), str(float)) -> utc, from timestamp.
        #     if is_timestamp(arg):
        #         return self.type.fromtimestamp(arg)

        #     # (Arrow) -> from the object's datetime.
        #     if isinstance(arg, Arrow):
        #         return self.type.fromdatetime(arg.datetime)

        #     # (datetime) -> from datetime.
        #     if isinstance(arg, datetime):
        #         return self.type.fromdatetime(arg)

        #     # (date) -> from date.
        #     if isinstance(arg, date):
        #         return self.type.fromdate(arg)

        #     # (tzinfo) -> now, @ tzinfo.
        #     elif isinstance(arg, tzinfo):
        #         return self.type.now(arg)

        #     # (str) -> now, @ tzinfo.
        #     elif isstr(arg):
        #         dt = parser.DateTimeParser(locale).parse_iso(arg)
        #         return self.type.fromdatetime(dt)

        #     # (struct_time) -> from struct_time
        #     elif isinstance(arg, struct_time):
        #         return self.type.utcfromtimestamp(calendar.timegm(arg))

        #     else:
        #         raise TypeError('Can\'t parse single argument type of \'{0}\''.format(type(arg)))

        # elif arg_count == 2:

        #     arg_1, arg_2 = args[0], args[1]

        #     if isinstance(arg_1, datetime):

        #         # (datetime, tzinfo) -> fromdatetime @ tzinfo/string.
        #         if isinstance(arg_2, tzinfo) or isstr(arg_2):
        #             return self.type.fromdatetime(arg_1, arg_2)
        #         else:
        #             raise TypeError('Can\'t parse two arguments of types \'datetime\', \'{0}\''.format(
        #                 type(arg_2)))

        #     # (date, tzinfo/str) -> fromdate @ tzinfo/string.
        #     elif isinstance(arg_1, date):

        #         if isinstance(arg_2, tzinfo) or isstr(arg_2):
        #             return self.type.fromdate(arg_1, tzinfo=arg_2)
        #         else:
        #             raise TypeError('Can\'t parse two arguments of types \'date\', \'{0}\''.format(
        #                 type(arg_2)))

        #     # (str, format) -> parse.
        #     elif isstr(arg_1) and (isstr(arg_2) or isinstance(arg_2, list)):
        #         dt = parser.DateTimeParser(locale).parse(args[0], args[1])
        #         return self.type.fromdatetime(dt, tzinfo=tzinfo)

        #     else:
        #         raise TypeError('Can\'t parse two arguments of types \'{0}\', \'{1}\''.format(
        #             type(arg_1), type(arg_2)))

        # # 3+ args -> datetime-like via constructor.
        # else:
        #     return self.type(*args, **kwargs)

		def local(self, *args, **kwargs):
			return self.get(*args, **kwargs).to('local')

		def datetime(self, *args, **kwargs):
			naive = kwargs.pop('naive', False)
			if len(args) == 1:
				arg = args[0]
				if isinstance(args[0], datetime.datetime):
					rv = arg
				elif isinstance(value, arrow.Arrow):
					rv = arg.datetime
				else:
					rv = self.get(*args, **kwargs).datetime
			else:
				rv = self.get(*args, **kwargs).datetime

			return rv.replace(tzinfo=None) if naive else rv
			

carbon = Factory(Carbon)


