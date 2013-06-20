#!/usr/bin/python
import os
import random
import string
from signal import signal, SIGPIPE, SIG_DFL

signal(SIGPIPE, SIG_DFL)

alpha = list(string.letters + string.digits)
min = 6
max = 10

if len(os.sys.argv) > 1:
	min = max = int(os.sys.argv[1])

while True:
	n = random.randint(min, max)
	p = ''
	for x in xrange(n):
		p += random.choice(alpha)
	try:
		print p
	except KeyboardInterrupt:
		os.sys.exit(0)
	except:
		os.sys.exit(1)
