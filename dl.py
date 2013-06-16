#!/usr/bin/python
#coding: utf-8

#Recursively downloads images from popular image boards.
#Only images will be saved on HDD. Only one thread is supported.
#Usage: dl.py path-to-save service additional arguments
#Examples:
#dl.py 2chan dat 45: 2chan photography board
#dl.py 2chan cgi k: fetch 2chan wallpapers board
#dl.py 2chan dat l: fetch 2chan wallpapers 2d board
#dl.py 2chan img 9: fetch 2chan problem consulting board
#dl.py 4chan hr: fetch 4chan high resolution board

import httplib2, urlparse
import re
import os, sys, os.path
from BeautifulSoup import BeautifulSoup as be
from time import time, strftime
h = httplib2.Http(timeout=15)

class main:
	def __init__(self, savePath, args):
		self.completed = []
		self.stats = {
			'done' : 0,
			'errorous' : 0,
			'saved' : 0,
			'skipped' : 0
			}
		images = re.compile('(image/png|image/jpeg|image/jpg|image/gif).*?')
		webpages = re.compile('(text/html|text/plain).*?')
		headers = { "User-Agent" : "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.2.16) Gecko/20110319 Firefox/3.6.16" }

		#service definitions:
		if args[0] == '2chan' and len(args) >= 3:
			self.links = [['http://' + args[1] + '.2chan.net/' + args[2] + '/', 0]]
			self.accept = re.compile('(http://.+\.2chan\.net/' + args[1] + '/' + args[2] + '/.+)|(http://.+\.2chan.net/(.+/)?res/.+\.htm)|(http://' + args[1] + '.2chan.net/' + args[2] + '/.+)')
			self.reject = re.compile('(http://' + args[1] + '.2chan.net/' + args[2] + '/res/futaba.+)')
		elif args[0] == '4chan' and len(args) >= 2:
			self.links = [['http://boards.4chan.org/' + args[1] + '/', 0]]
			self.accept = re.compile('(http://boards\.4chan\.org/[a-z0-9]+/res/\d+$)|(http://boards\.4chan\.org/[a-z0-9]+/\d+$)|(http://images\.4chan\.org/[a-z0-9]+/src/.+)')
			self.reject = re.compile('-')
		elif args[0] == 'gelbooru' and len(args) >= 2:
			self.links = [['http://gelbooru.com/index.php?page=post&s=list&tags=' + args[1] + '&pid=0', 0]]
			self.accept = re.compile('http://([a-z0-9]+\.)?gelbooru.com/(index.php\?page=post&s=list&tags=.+&pid=.+|index.php\?page=post&s=view&id=.+|/?images/[/a-f0-9]+\.[a-z]{3})')
			self.reject = re.compile('-')
		else:
			print 'service not recognized'
			os.sys.exit(0)


		while self.links:
			#prepare and filter top link
			self.stats['done'] += 1
			link, distance = self.links.pop()
			path = savePath + '/' + link.replace('http://', '')
			path = path.replace('?', '@')
			path = path.replace('\\', '/')
			while (path.find('//') > 0):
				path = path.replace('//', '/')
			for char in list(':*"<>|'):
				path = path.replace(char, '_')
			print "\t" * distance + link, '(' + strftime('%H:%M:%S') + ' ' + repr(len(self.links) + 1) + '+):',

			if os.path.isfile(path):
				self.stats['skipped'] += 1
				print 'already saved'
				continue
			if link in self.completed:
				self.stats['skipped'] += 1
				print 'already checked'
				continue


			#download
			try:
				resp, content = h.request(link, 'GET', headers=headers)
				#content = content.decode('utf-8')
			except KeyboardInterrupt:
				print "Bye"
				sys.exit(1)
			except Exception as inst:
				self.stats['errorous'] += 1
				print >>sys.stderr, 'error:', inst
				continue
			print resp['status'] + ';',
			if resp['status'] != '200':
				print ''
				self.stats['errorous'] += 1
				continue
			self.completed.append([link, distance])

			#decide what to do
			if images.match(resp['content-type']):
				print 'saving...',
				folder = os.path.dirname(path)
				if not os.path.isdir(folder):
					os.makedirs(folder)
				try:
					f = open(path, 'wb')
					f.write(content)
					f.close()
					self.stats['saved'] += 1
					print 'ok'
				except:
					self.stats['errorous'] += 1
					print >>sys.stderr, 'error while saving to', path, '(folders:', folder + ')'
			elif webpages.match(resp['content-type']):
				self.stats['skipped'] += 1
				print 'reading links...',
				soup = be(content)
				localStats = {
					'added' : 0,
					'unmatched' : 0,
					'onlist' : 0
					}
				for elem in soup.findAll('a', href=True):
					link2 = urlparse.urljoin(link, elem.get('href'))
					if not self.accept.match(link2) or self.reject.match(link2):
						localStats['unmatched'] += 1
						continue
					if link2 in sum(self.links, []) or link2 in sum(self.completed, []):
						localStats['onlist'] += 1
						continue
					self.links.append([link2, distance + 1])
					localStats['added'] += 1
				print repr(localStats['added']) + ' added, ' + repr(localStats['onlist']) + ' on list'
			else:
				self.stats['skipped'] += 1
				print 'ignoring'

	def __del__(self):
		print 'Done:', self.stats['done']
		print 'Saved:', self.stats['saved']
		print 'Skipped:', self.stats['skipped']
		print 'Errorous:', self.stats['errorous']

if __name__ == '__main__':
	main(sys.argv[1], sys.argv[2:])
