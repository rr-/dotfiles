#!/usr/bin/python3
# -*- coding: utf-8 -*-
import sys
from lib.dt import get_month_day_range, parse
from datetime import datetime, timedelta

def monthdelta(d1, d2):
	delta = 0
	inv = False
	if d1 > d2:
		d1, d2 = d2, d1
		inv = True
	while d1 < d2:
		d1 += timedelta(days=1)
		month_range = list(get_month_day_range(d1))
		last_day = month_range[-1].day
		delta += 1 / last_day
	if inv:
		delta *= -1
	return delta

if len(sys.argv) == 1:
	print('No date specified', file=sys.stderr)
	sys.exit(1)

try:
	date1 = parse(sys.argv[1])
	if len(sys.argv) == 2:
		date2 = datetime.now()
	else:
		date2 = parse(sys.argv[2])
except ValueError:
	print('Invalid date format', file=sys.stderr)
	sys.exit(1)

diff = date2 - date1
print(date2, '-', date1)
print('Seconds: {0:.2f}'.format(diff.days * 24 * 60 * 60 + diff.seconds))
print('Minutes: {0:.2f}'.format(diff.days * 24 * 60 + diff.seconds / 60))
print('Hours:   {0:.2f}'.format(diff.days * 24 + diff.seconds / 60 / 60))
print('Days:    {0:.2f}'.format(diff.days))
print('Months:  {0:.2f}'.format(monthdelta(date1, date2)))
print('Years:   {0:.2f}'.format(monthdelta(date1, date2) / 12))
