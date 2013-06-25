#!/usr/bin/python3
# -*- coding: utf-8 -*-

import lib.colors as colors

columns = 4
low = 0
up = 128
items = \
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
	127: {'short': 'DEL'},
}

#fill the rest of the ascii table
for i in range(low, up):
	if i not in items:
		items[i] = {'short': chr(i), 'color': ['Fore.RED']}
	else:
		items[i]['color'] = ['Fore.GREEN']
	items[i]['char'] = i

#compute column padding
pads = {}
max_y = (up - low) // columns
for x in range(columns):
	column = [items[y + x * max_y + low] for y in range(0, max_y)]
	pad1 = max(len(str(item['char'])) for item in column)
	pad2 = max(len(item['short']) for item in column)
	pad3 = max(len(item['long']) if 'long' in item else 0 for item in column)
	if pad3 > 0:
		pad3 += 2 #add space for brackets
	pads[x] = (pad1, pad2, pad3)

#print the table
for y in range(max_y):
	for x in range(columns):
		pad1, pad2, pad3 = pads[x]
		item = items[y + x * max_y + low]
		print(str(item['char']).ljust(pad1), end=' ')
		print('x{0:02X}'.format(item['char']), end=' ')
		print(colors.colorize(item['short'].ljust(pad2), item['color']), end=' ')
		if 'long' in item:
			print(('({0})'.format(item['long'])).ljust(pad3), end=' ')
		else:
			print(''.ljust(pad3), end=' ')
		if x != columns - 1:
			print(colors.colorize('|', ['Fore.WHITE']), end=' ')
	print()
