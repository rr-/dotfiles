#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
#  Copyright (C) 2009 Arkadiusz MiĹ�kiewicz <arekm@pld-linux.org>
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import sys
import urllib.request, urllib.parse, urllib.error
import subprocess
import tempfile
import os
import getopt

try:
	from hashlib import md5 as md5
except ImportError:
	from md5 import md5

napipass = 'iBlm8NTigvru0Jr0'
prog = os.path.basename(sys.argv[0])

video_files = [ 'asf', 'avi', 'divx', 'mkv', 'mp4', 'mpeg', 'mpg', 'ogm', 'rm', 'rmvb', 'wmv' ]
languages = { 'pl': 'PL', 'en': 'ENG' }

def f(z):
	idx = [ 0xe, 0x3,  0x6, 0x8, 0x2 ]
	mul = [   2,   2,    5,   4,   3 ]
	add = [   0, 0xd, 0x10, 0xb, 0x5 ]
	b = []
	for i in range(len(idx)):
		a = add[i]
		m = mul[i]
		i = idx[i]
		t = a + int(z[i], 16)
		v = int(z[t:t+2], 16)
		b.append( ("%x" % (v*m))[-1] )
	return ''.join(b)

def usage():
	print("Usage: %s [OPTIONS]... [FILE|DIR]..." % prog, file=sys.stderr)
	print("Find video files and download matching subtitles from napiprojekt server.", file=sys.stderr)
	print(file=sys.stderr)
	print("Supported options:", file=sys.stderr)
	print("     -h, --help            display this help and exit", file=sys.stderr)
	print("     -l, --lang=LANG       subtitles language", file=sys.stderr)
	print(file=sys.stderr)

def main(argv=sys.argv):

	try:
		opts, args = getopt.getopt(argv[1:], "hl:nu", ["help", "lang"])
	except getopt.GetoptError as err:
		print(str(err))
		usage()
		return 2

	output = None
	verbose = False
	lang = 'pl'
	for o, a in opts:
		if o == "-v":
			verbose = True
		elif o in ("-h", "--help"):
			usage()
			return 0
		elif o in ("-l", "--lang"):
			if a in languages:
				lang = a
			else:
				print("%s: unsupported language `%s'. Supported languages: %s" % (prog, a, str(list(languages.keys()))), file=sys.stderr)
				return 1
		else:
			print("%s: unhandled option" % prog, file=sys.stderr)
			return 1

	print("%s: Subtitles language `%s'. Finding video files..." % (prog, lang), file=sys.stderr)

	files = []
	for arg in args:
		if os.path.isdir(arg):
			for dirpath, dirnames, filenames in os.walk(arg, topdown=False):
				for file in filenames:
					if file[-4:-3] == '.' and file.lower()[-3:] in video_files:
						files.append(os.path.join(dirpath, file))
		else:
			files.append(arg)

	files.sort()

	i_total = len(files)
	i = 0

	for file in files:
		i += 1

		vfile = file + '.sub'
		if len(file) > 4:
			vfile = file[:-4] + '.sub'

		print("%s: %d/%d: Processing subtitle for %s" % (prog, i, i_total, file), file=sys.stderr)

		d = md5()
		try:
			d.update(open(file, 'rb').read(10485760))
		except (IOError, OSError) as e:
			print("%s: %d/%d: Hashing video file failed: %s" % (prog, i, i_total, e), file=sys.stderr)
			continue

		url = "http://napiprojekt.pl/unit_napisy/dl.php?l=%s&f=%s&t=%s&v=other&kolejka=false&nick=&pass=&napios=%s" % \
			(languages[lang], d.hexdigest(), f(d.hexdigest()), os.name)

		sub = None
		http_code = 200
		try:
			sub = urllib.request.urlopen(url)
			if hasattr(sub, 'getcode'):
				http_code = sub.getcode()
			sub = sub.read()
		except (IOError, OSError) as e:
			print("%s: %d/%d: Fetching subtitle failed: %s" % (prog, i, i_total, e), file=sys.stderr)
			continue

		if http_code != 200:
			print("%s: %d/%d: Fetching subtitle failed, HTTP code: %s" % (prog, i, i_total, str(http_code)), file=sys.stderr)
			continue

		if str(sub).startswith('NPc'):
			print("%s: %d/%d: Subtitle NOT FOUND" % (prog, i, i_total), file=sys.stderr)
			continue

		fp = open('Z:/hub/napisy.7z', 'wb')
		fp.write(sub)
		tfp = fp.name
		fp.flush()
		fp.close()

		try:
			cmd = ['/usr/bin/7z', 'x', '-y', '-so', '-p' + napipass, tfp]
			sa = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, close_fds=True)
			(so, se) = sa.communicate(sub)
			retcode = sa.returncode
		except OSError as e:
			se = e
			retcode = True

		os.unlink(tfp)


		if retcode:
			print("%s: %d/%d: Subtitle decompression FAILED: %s" % (prog, i, i_total, se), file=sys.stderr)
			continue

		fp = open(vfile, 'wb')
		fp.write(so)
		fp.close()

		print("%s: %d/%d: STORED (%d bytes)" % (prog, i, i_total, len(so)), file=sys.stderr)

	return 0

if __name__ == "__main__":
	ret = None
	try:
		ret = main()
	except (KeyboardInterrupt, SystemExit):
		print("%s: Interrupted, aborting." % prog, file=sys.stderr)
	sys.exit(ret)
