#!/usr/bin/python
import sys
from calendar import monthrange
from datetime import datetime, timedelta

if len(sys.argv) == 1:
	print >>sys.stderr, 'No date specified'
	sys.exit(1)

def monthdelta(d1, d2):
	delta = 0
	while True:
		mdays = monthrange(d1.year, d1.month)[1]
		d1 += timedelta(days=mdays)
		if d1 <= d2:
			delta += 1
		else:
			break
	return delta

def parse(s):
	if '-' not in s:
		s = datetime.strftime(datetime.now(), '%Y-%m-%d ') + s
	try:
		return datetime.strptime(s, '%Y-%m-%d %H:%M:%S')
	except:
		try:
			return datetime.strptime(s, '%Y-%m-%d %H:%M')
		except:
			return datetime.strptime(s, '%Y-%m-%d')

date1 = parse(sys.argv[1])
if len(sys.argv) == 2:
	date2 = datetime.now()
else:
	date2 = parse(sys.argv[2])
print date1

diff = date1 - date2
print 'Seconds: ' + str(diff.days * 24 * 60 * 60 + diff.seconds)
print 'Minutes: ' + str(diff.days * 24 * 60 + diff.seconds / 60)
print 'Hours:   ' + str(diff.days * 24 + diff.seconds / 60 / 60)
print 'Days:    ' + str(diff.days)
if date2 < date1:
	print 'Months:  ' + str(monthdelta(date2, date1))
	print 'Years:   ' + str(monthdelta(date2, date1) / 12)
else:
	print 'Months:  -' + str(monthdelta(date1, date2))
	print 'Years:   -' + str(monthdelta(date1, date2) / 12)
