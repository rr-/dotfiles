#!/usr/bin/python
# -*- coding: utf-8 -*-

import lib.colors as colors

columns = 4
low = 0
up = 128
definitions = \
{
	0:   {'short': 'NUL', 'long': 'null'},
	1:   {'short': 'SOH', 'long': 'start of heading'},
	2:   {'short': 'STX', 'long': 'start of text'},
	3:   {'short': 'ETX', 'long': 'end of text'},
	4:   {'short': 'EOT', 'long': 'end of transmission'},
	5:   {'short': 'ENQ', 'long': 'enquiry'},
	6:   {'short': 'ACK', 'long': 'acknowledge'},
	7:   {'short': 'BEL', 'long': 'bell'},
	8:   {'short': 'BS',  'long': 'backspace'},
	9:   {'short': 'TAB', 'long': 'horizontal tab'},
	10:  {'short': 'LF',  'long': 'new line'},
	11:  {'short': 'VT',  'long': 'vertical tab'},
	12:  {'short': 'FF',  'long': 'new page'},
	13:  {'short': 'CR',  'long': 'carriage return'},
	14:  {'short': 'SO',  'long': 'shift out'},
	15:  {'short': 'SI',  'long': 'shift in'},
	16:  {'short': 'DLE', 'long': 'data link escape'},
	17:  {'short': 'DC1', 'long': 'device control 1'},
	18:  {'short': 'DC2', 'long': 'device control 2'},
	19:  {'short': 'DC3', 'long': 'device control 3'},
	20:  {'short': 'DC4', 'long': 'device control 4'},
	21:  {'short': 'NAK', 'long': 'negative acknowledge'},
	22:  {'short': 'SYN', 'long': 'synchronous idle'},
	23:  {'short': 'ETB', 'long': 'end of trans. block'},
	24:  {'short': 'CAN', 'long': 'cancel'},
	25:  {'short': 'EM',  'long': 'end of medium'},
	26:  {'short': 'SUB', 'long': 'substitue'},
	27:  {'short': 'ESC', 'long': 'escape'},
	28:  {'short': 'FS',  'long': 'file separator'},
	29:  {'short': 'GS',  'long': 'group separator'},
	30:  {'short': 'RS',  'long': 'record separator'},
	31:  {'short': 'US',  'long': 'unit separator'},
	32:  {'short': ' '},
	127: {'short': 'DEL'},
}

table = {}

for x in xrange(columns):
	max_y = (up - low) / columns

	column = []
	for y in xrange(max_y):
		c = x * max_y + y + low

		cell = {}
		cell['char'] = c
		if c in definitions:
			definition = definitions[c]
			cell['color'] = ['Fore.GREEN']
			cell['short'] = definition['short']
			if 'long' in definition:
				cell['long'] = definition['long']
			else:
				cell['long'] = ''
		else:
			cell['color'] = ['Fore.RED']
			cell['short'] = chr(c)
			cell['long'] = ''

		column.append(cell)

	pad1 = max(len(str(column[y]['char'])) for y in xrange(max_y))
	pad2 = max(len(column[y]['short']) for y in xrange(max_y))
	pad3 = max(len(column[y]['long']) for y in xrange(max_y))
	for y in xrange(max_y):
		cell = column[y]
		text = ''
		text += '%0*d' % (pad1, cell['char']) + ' '
		text += 'x%02X' % cell['char'] + ' '
		text += colors.colorize('%-*s' % (pad2, cell['short']) + ' ', cell['color'])
		if pad3 > 0:
			text += '(%s)%-*s' % (cell['long'], pad3 + 1 - len(cell['long']), ' ')
		if x != columns - 1:
			text += colors.colorize('|', ['Fore.WHITE'])
		table[x, y] = text

for y in xrange((up - low) / columns):
	for x in xrange(columns):
		print table[x,y],
	print
