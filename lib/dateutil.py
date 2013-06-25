import datetime
import dateutil.parser

def parse(string):
	return dateutil.parser.parse(string)

def date_range(start_date, end_date):
	for n in range((end_date - start_date).days + 1):
		yield start_date + datetime.timedelta(days=n)

def get_month_day_range(date):
	first_day = datetime.date(date.year, date.month, 1)
	nm = datetime.date(date.year, date.month, 15) + datetime.timedelta(days=31)
	last_day = datetime.date(nm.year, nm.month, 1) - datetime.timedelta(days=1)
	return date_range(first_day, last_day)
