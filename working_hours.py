#!/usr/bin/python
# -*- coding: utf-8 -*-
import datetime
import getpass
import locale
import gdata.calendar.client
import sys
from pyExcelerator import *
from dateutil.parser import parse

def date_range(start_date, end_date):
	for n in range((end_date - start_date).days + 1):
		yield start_date + datetime.timedelta(days=n)

def get_month_day_range(date):
	first_day = datetime.date(date.year, date.month, 1)
	nm = datetime.date(date.year, date.month, 15) + datetime.timedelta(days=31)
	last_day = datetime.date(nm.year, nm.month, 1) - datetime.timedelta(days=1)
	return date_range(first_day, last_day)

class GodzinyMaker(object):
	def __init__(self, mail, password, keyword, path):
		hours = self.getWorkingHours(mail, password, keyword)
		for row in hours.values():
			print \
				row[0].strftime('%Y-%m-%d %H:%M:%S'), '-', \
				row[1].strftime('%Y-%m-%d %H:%M:%S')
		self.saveSpreadsheet(hours, path)

	def getWorkingHours(self, mail, password, keyword):
		client = gdata.calendar.client.CalendarClient(source='working-hours-client')
		client.ClientLogin(mail, password, client.source)

		feed = client.GetAllCalendarsFeed()
		for i, cal in enumerate(feed.entry):
			if cal.title.text.lower().find(keyword.lower()) > 0:
				calendarUrl = cal.content.src
				break
		if calendarUrl is None:
			raise Exception('No valid calendar found.')

		hours = {}

		query = gdata.calendar.client.CalendarEventQuery()
		dayRange = list(get_month_day_range(datetime.date.today()))
		query.start_min, query.start_max = dayRange[0], dayRange[-1]
		feed = client.GetCalendarEventFeed(q=query, uri=calendarUrl)
		for i, event in enumerate(feed.entry):
			for when in event.when:
				start = parse(when.start)
				end = parse(when.end)
				key = datetime.date.strftime(start, '%Y-%m-%d')
				hours[key] = [start, end]

		return hours



	def initSpreadsheet(self):
		self.normalFont = Font()
		self.normalFont.name = 'Arial'
		self.normalFont.colour_index = 0
		self.normalFont.bold = False
		self.boldFont = Font()
		self.boldFont.name = self.normalFont.name
		self.boldFont.colour_index = self.normalFont.colour_index
		self.boldFont.bold = True
		self.bordersNone = Borders()
		self.borders = Borders()
		self.borders.left = 6
		self.borders.right = 6
		self.borders.top = 6
		self.borders.bottom = 6
		self.alRight = Alignment()
		self.alRight.horz = Alignment.HORZ_RIGHT
		self.alRight.vert = Alignment.VERT_CENTER
		self.alMiddle = Alignment()
		self.alMiddle.horz = Alignment.HORZ_CENTER
		self.alMiddle.vert = Alignment.VERT_CENTER
		self.alLeft = Alignment()
		self.alLeft.horz = Alignment.HORZ_LEFT
		self.alLeft.vert = Alignment.VERT_CENTER


	def writeHeader(self, ws):
		style = XFStyle()
		style.font = self.normalFont
		style.alignment = self.alRight
		ws.write_merge(0, 0, 0, 5, u'Poznań, %sr.' % datetime.date.today().strftime('%d.%m.%Y'), style)

		style = XFStyle()
		style.font = self.normalFont
		style.alignment = self.alMiddle
		ws.write_merge(3, 3, 1, 3, u'Rozliczenie za:', style)
		ws.write_merge(5, 5, 1, 3, u'Zleceniobiorca:', style)
		style.alignment = self.alLeft
		style.font = self.boldFont
		ws.write(3, 4, datetime.date.today().strftime('%B %Yr.').decode('utf-8'), style)
		ws.write(5, 4, u'Marcin Kurczewski', style)


	def writeHoursTable(self, ws, hours):
		style = XFStyle()
		style.font = self.boldFont
		style.borders = self.borders
		style.alignment = self.alMiddle
		ws.write(9, 1, u'L.p.', style)
		ws.write(9, 2, u'Od', style)
		ws.write(9, 3, u'Do', style)
		ws.write(9, 4, u'Ilość godzin', style)
		ws.write(9, 5, u'Data', style)

		row = 10
		i = 1
		style.font = self.normalFont
		dayRange = list(get_month_day_range(datetime.date.today()))
		firstDay, lastDay = dayRange[0], dayRange[-1]
		for date in dayRange:
			ws.write(row, 1, i, style)
			ws.write(row, 5, u'%sr.' % date.strftime('%d.%m.%Y'), style)
			#todo fetch actual hours
			key = date.strftime('%Y-%m-%d')
			if key in hours:
				hour1, hour2 = hours[key]
			else:
				hour1 = None
				hour2 = None
			if hour1 is None or hour2 is None:
				ws.write(row, 2, u'-', style)
				ws.write(row, 3, u'-', style)
				ws.write(row, 4, u'-', style)
			else:
				delta = hour2 - hour1
				ws.write(row, 2, hour1.strftime('%H:%M:%S'), style)
				ws.write(row, 3, hour2.strftime('%H:%M:%S'), style)
				ws.write(row, 4, delta.seconds // 3600, style)
			row += 1
			i += 1

		style.alignment = self.alRight
		style.borders = self.bordersNone
		style.font = self.normalFont
		ws.write_merge(row, row, 1, 3, u'Łączna liczba godzin:', style)

		style.alignment = self.alMiddle
		style.font = self.boldFont
		ws.write(row, 4, Formula('SUM(E11:E' + str(row) + ')'), style)


	def writeFooter(self, ws):
		style = XFStyle()
		style.alignment = self.alMiddle
		style.font = self.normalFont
		ws.write_merge(45, 45, 1, 2, u'.' * 35, style)
		ws.write_merge(45, 45, 4, 5, u'.' * 35, style)
		ws.write_merge(46, 46, 1, 2, u'(podpis zleceniobiorcy)', style)
		ws.write_merge(46, 46, 4, 5, u'(podpis kierownika)', style)



	def saveSpreadsheet(self, hours, path):
		self.initSpreadsheet()
		wb = Workbook()
		ws = wb.add_sheet('sheet0')

		self.writeHeader(ws)
		self.writeHoursTable(ws, hours)
		self.writeFooter(ws)

		wb.save(path)

if __name__ == '__main__':
	locale.setlocale(locale.LC_ALL, 'pl_PL.UTF-8')
	mail = 'mkurczew@gmail.com'
	password = getpass.getpass()
	keyword = 'forcom'
	if len(sys.argv) >= 1:
		path = sys.argv[1]
	else:
		path = 'working-hours.xls'
	GodzinyMaker(mail, password, keyword, path)
