#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import time
import subprocess
import tempfile
import urllib
import datetime
from lib.proc import execute
from lib.string import clean_screen_name

#settings
user = 'rr-'
host = 'burza'
src_folder = '/cygdrive/z/hub/pinkyard/queued/'
safe_folder = '/cygdrive/z/hub/pinkyard/done/'

folder = datetime.date.today().strftime('%Y-%m')
dst_folder = '/srv/www/pinkyard/public_html/files/%s/' % folder
resolver_url = 'http://pink.sakuya.pl/resolve/%s/' % folder

#prepare commands
commands = []
y = ''
for x in dst_folder.strip('/').split('/'):
	y += '/' + x
	commands.append('-mkdir "{0}"'.format(y))

items = []
for name in os.listdir(src_folder):
	item = {}
	item['src_name'] = name
	item['src_path'] = os.path.join(src_folder, item['src_name'])
	if not os.path.isfile(item['src_path']):
		continue
	item['src_time'] = os.stat(item['src_path'])
	item['dst_name'] = clean_screen_name(item['src_name'])
	item['dst_path'] = os.path.join(dst_folder, item['dst_name'])
	item['safe_path'] = os.path.join(safe_folder, item['src_name'])
	item['resolver_url'] = resolver_url + urllib.quote(item['dst_name'])
	items.append(item)
if len(items) == 0:
	os.sys.exit(0)

for i, item in enumerate(sorted(items, key=lambda f: f['src_time'])):
	future = time.mktime((datetime.datetime.now() + datetime.timedelta(seconds=i)).timetuple())
	os.utime(item['src_path'], (future, future))
	commands.append('put -p "%s" "%s"' % (item['src_path'], item['dst_path']))
	commands.append('chmod 0744 "%s"' % item['dst_path'])

#write file, execute sftp
cmds_file = tempfile.TemporaryFile()
cmds_file.write("\n".join(commands))
cmds_file.flush()

status, output, _ = execute(['sftp', '-b', cmds_file.name, user + '@' + host])
print >>os.sys.stderr, output
cmds_file.close()

if status == 0:
	for item in items:
		try:
			os.rename(item['src_path'], item['safe_path'])
		except:
			print >>os.sys.stderr, 'Error renaming', item['src_path'], 'to', item['safe_path']
		print execute(['wget', '-qO-', item['resolver_url']])[1]
