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

#fill the rest of the ascii table
for i in xrange(low, up):
	if not i in definitions:
		definition = {'short': chr(i)}
		definitions[i] = definition
		definitions[i]['color'] = ['Fore.RED']
	else:
		definitions[i]['color'] = ['Fore.GREEN']
	definitions[i]['char'] = i

#compute column padding
pads = {}
max_y = (up - low) / columns
for x in xrange(columns):
	column = [definitions[y + x * max_y + low] for y in xrange(0, max_y)]
	pad1 = max(len(str(definition['char'])) for definition in column)
	pad2 = max(len(definition['short']) for definition in column)
	pad3 = max(len(definition['long']) if 'long' in definition else 0 for definition in column)
	if pad3 > 0:
		pad3 += 2 #add spaces for brackets
	pads[x] = (pad1, pad2, pad3)

#print the table
for y in xrange(max_y):
	for x in xrange(columns):
		pad1, pad2, pad3 = pads[x]
		definition = definitions[x * max_y + y + low]
		print str(definition['char']).ljust(pad1),
		print 'x%02X' % definition['char'],
		print colors.colorize(definition['short'].ljust(pad2), definition['color']),
		if 'long' in definition:
			print ('(%s)' % definition['long']).ljust(pad3),
		else:
			print ''.ljust(pad3),
		if x != columns - 1:
			print colors.colorize('|', ['Fore.WHITE']),
	print
