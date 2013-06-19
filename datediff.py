#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import dateutil.parser
from calendar import monthrange
from datetime import datetime, timedelta

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

if len(sys.argv) == 1:
	print >>sys.stderr, 'No date specified'
	sys.exit(1)

try:
	date1 = dateutil.parser.parse(sys.argv[1])
	if len(sys.argv) == 2:
		date2 = datetime.now()
	else:
		date2 = dateutil.parser.parse(sys.argv[2])
except ValueError:
	print >>sys.stderr, 'Invalid date format'
	sys.exit(1)

diff = date2 - date1
print date2, '-', date1
print 'Seconds: ' + str(diff.days * 24 * 60 * 60 + diff.seconds)
print 'Minutes: ' + str(diff.days * 24 * 60 + diff.seconds / 60)
print 'Hours:   ' + str(diff.days * 24 + diff.seconds / 60 / 60)
print 'Days:    ' + str(diff.days)
if date1 < date2:
	print 'Months:  ' + str(monthdelta(date1, date2))
	print 'Years:   ' + str(monthdelta(date1, date2) / 12)
else:
	print 'Months:  -' + str(monthdelta(date2, date1))
	print 'Years:   -' + str(monthdelta(date2, date1) / 12)
