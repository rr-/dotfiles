#!/usr/bin/python
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
import urllib
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
	for i in xrange(len(idx)):
		a = add[i]
		m = mul[i]
		i = idx[i]

		t = a + int(z[i], 16)
		v = int(z[t:t+2], 16)
		b.append( ("%x" % (v*m))[-1] )

	return ''.join(b)

def usage():
	print >> sys.stderr, "Usage: %s [OPTIONS]... [FILE|DIR]..." % prog
	print >> sys.stderr, "Find video files and download matching subtitles from napiprojekt server."
	print >> sys.stderr
	print >> sys.stderr, "Supported options:"
	print >> sys.stderr, "     -h, --help            display this help and exit"
	print >> sys.stderr, "     -l, --lang=LANG       subtitles language"
	print >> sys.stderr, "     -n, --nobackup        make no backup when in update mode"
	print >> sys.stderr, "     -u, --update          fetch new and also update existing subtitles"
	print >> sys.stderr
	print >> sys.stderr, "pynapi $Revision: 1.27 $"
	print >> sys.stderr
	print >> sys.stderr, "Report bugs to <arekm@pld-linux.org>."

def main(argv=sys.argv):

	try:
		opts, args = getopt.getopt(argv[1:], "hl:nu", ["help", "lang", "nobackup", "update"])
	except getopt.GetoptError, err:
		print str(err)
		usage()
		return 2

	output = None
	verbose = False
	nobackup = False
	update = False
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
				print >> sys.stderr, "%s: unsupported language `%s'. Supported languages: %s" % (prog, a, str(languages.keys()))
				return 1
		elif o in ("-n", "--nobackup"):
			nobackup = True
		elif o in ("-u", "--update"):
			update = True
		else:
			print >> sys.stderr, "%s: unhandled option" % prog
			return 1

	print >> sys.stderr, "%s: Subtitles language `%s'. Finding video files..." % (prog, lang)

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

		if not update and os.path.exists(vfile):
			continue

		if not nobackup and os.path.exists(vfile):
			vfile_bak = vfile + '-bak'
			try:
				os.rename(vfile, vfile_bak)
			except (IOError, OSError), e:
				print >> sys.stderr, "%s: Skipping due to backup of `%s' as `%s' failure: %s" % (prog, vfile, vfile_bak, e)
				continue
			else:
				print >> sys.stderr, "%s: Old subtitle backed up as `%s'" % (prog, vfile_bak)

		print >> sys.stderr, "%s: %d/%d: Processing subtitle for %s" % (prog, i, i_total, file)

		d = md5()
		try:
			d.update(open(file).read(10485760))
		except (IOError, OSError), e:
			print >> sys.stderr, "%s: %d/%d: Hashing video file failed: %s" % (prog, i, i_total, e)
			continue

		url = "http://napiprojekt.pl/unit_napisy/dl.php?l=%s&f=%s&t=%s&v=other&kolejka=false&nick=&pass=&napios=%s" % \
			(languages[lang], d.hexdigest(), f(d.hexdigest()), os.name)

		sub = None
		http_code = 200
		try:
			sub = urllib.urlopen(url)
			if hasattr(sub, 'getcode'):
				http_code = sub.getcode()
			sub = sub.read()
		except (IOError, OSError), e:
			print >> sys.stderr, "%s: %d/%d: Fetching subtitle failed: %s" % (prog, i, i_total, e)
			continue

		if http_code != 200:
			print >> sys.stderr, "%s: %d/%d: Fetching subtitle failed, HTTP code: %s" % (prog, i, i_total, str(http_code))
			continue

		if sub.startswith('NPc'):
			print >> sys.stderr, "%s: %d/%d: Subtitle NOT FOUND" % (prog, i, i_total)
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
		except OSError, e:
			se = e
			retcode = True

		os.unlink(tfp)


		if retcode:
			print >> sys.stderr, "%s: %d/%d: Subtitle decompression FAILED: %s" % (prog, i, i_total, se)
			continue

		fp = open(vfile, 'w')
		fp.write(so)
		fp.close()

		print >> sys.stderr, "%s: %d/%d: STORED (%d bytes)" % (prog, i, i_total, len(so))

	return 0

if __name__ == "__main__":
	ret = None
	try:
		ret = main()
	except (KeyboardInterrupt, SystemExit):
		print >> sys.stderr, "%s: Interrupted, aborting." % prog
	sys.exit(ret)
