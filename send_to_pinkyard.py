#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os
import urllib.request, urllib.parse, urllib.error
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

items = []
for name in os.listdir(src_folder):
	item = {}
	item['src_name'] = name
	item['src_path'] = os.path.join(src_folder, item['src_name'])
	if not os.path.isfile(item['src_path']):
		continue
	item['src_time'] = os.stat(item['src_path'])
	item['dst_name'] = clean_screen_name(item['src_name']).replace('\'', '')
	item['dst_path'] = os.path.join(dst_folder, item['dst_name'])
	item['safe_path'] = os.path.join(safe_folder, item['src_name'])
	item['resolver_url'] = resolver_url + urllib.parse.quote(item['dst_name'])
	items.append(item)
if len(items) == 0:
	os.sys.exit(0)

#make remote destination directory
execute(['ssh', '%s@%s' % (user, host), 'bash -c \'mkdir -p "%s"\'' % dst_folder])
execute(['ssh', '%s@%s' % (user, host), 'bash -c \'chmod 0755 "%s"\'' % dst_folder])

for i, item in enumerate(sorted(items, key=lambda item: item['src_time'])):
	#transfer the file
	execute(['scp', item['src_path'], '%s@%s:%s' % (user, host, item['dst_path'])])

	#update file stats
	future = datetime.datetime.now() + datetime.timedelta(seconds=i)
	execute(['ssh', '%s@%s' % (user, host), 'bash -c \'touch "%s" -d "%s"\'' % (item['dst_path'], future.strftime('%Y-%m-%d %H:%M:%S'))])
	execute(['ssh', '%s@%s' % (user, host), 'bash -c \'chmod 0644 "%s"\'' % item['dst_path']])

	#move the file
	try:
		os.rename(item['src_path'], item['safe_path'])
	except:
		print('Error renaming', item['src_path'], 'to', item['safe_path'], file=sys.stderr)
	print(execute(['wget', '-qO-', item['resolver_url']])[1])
