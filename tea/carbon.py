import datetime
import time
from pytz import timezone

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
	return str(n)+('th' if 4 <= m100 <= 20 else small.get(m10, 'th'))

def strformat(dtm, f):
	return dtm.strftime(f).replace('{th}', ordinal(dtm.day))


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
	f = '%b {th}, %Y'
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

	return strformat(dtm, f) # dtm.strftime(f)



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