#!/usr/bin/python
#coding: utf-8
#helper script for dl.py. recursively checks files in input path whether they still
#exist on the internet; if not (i.e. 404 error occured), moves them to output path.
#supports multithreading for faster checking.
#files in input path should be named in wget fashion: assuming input path was
#/home/chr/dl/,  file representing http://www.example.com/subfolder/image.jpg should
#be stored as /home/chr/dl/www.example.com/subfolder/image.jpg.

import os, sys, time
import socket
import threading
import httplib
import shutil
from threading import Thread
from httplib import HTTPException

paths = []

class main:
	def __init__(self, inPath, outPath):
		self.populating = True
		self.die = False
		self.stats = {
			'done' : 0,
			'max' : 0,
			'touched' : 0,
			'moved' : 0,
			'errorous' : 0,
			'timeout' : 0,
			'skipped' : 0
			}
		self.lock = threading.RLock()

		threads = []
		for i in range(4):
			t = Thread(target = self.checkPaths)
			threads.append(t)
			t.start()

		print 'Script will populate files in background.'
		try:
			self.populateFiles(inPath, outPath)
		except KeyboardInterrupt:
			self.die = True
			raise
		self.populating = False

		while len(threads) > 0:
			try:
				threads = [t.join(1) for t in threads if t is not None and t.isAlive()]
			except KeyboardInterrupt:
				self.die = True

	def checkPaths(self):
		conn = None
		lastHost = ''
		while True:
			with self.lock:
				if self.die:
					print 'Breaking'
					break
				if self.stats['done'] >= self.stats['max']:
					if self.populating:
						continue
					else:
						break
				path = paths[self.stats['done']]
				os.sys.stdout.write("\033[K \rDone: %(done)d/%(max)d (moved: %(moved)d, touched: %(touched)d, skipped: %(skipped)d, errorous: %(errorous)d, timeout: %(timeout)d)" % self.stats)
				os.sys.stdout.flush()
				self.stats['done'] += 1

				#skip
				if time.time() - os.path.getmtime(path['src']) < 12 * 60 * 60:
					self.stats['skipped'] += 1
					continue

			#get response
			if lastHost != path['host'] or not conn:
				try:
					conn = httplib.HTTPConnection(path['host'])
				#except KeyboardInterrupt:
				#	with self.lock: self.stats['skipped'] += 1
				#	break
				except socket.timeout:
					with self.lock: self.stats['timeout'] += 1
					conn = None
					continue
				except Exception as inst:
					with self.lock:
						print inst
						print sys.exc_info()
						self.stats['errorous'] += 1
					conn = None
					continue
			try:
				conn.request("HEAD", path['url'])
				res = conn.getresponse()
				status = res.status
			except KeyboardInterrupt:
				with self.lock: self.stats['skipped'] += 1
				break
			except Exception as inst:
				with self.lock:
					print inst
					print sys.exc_info()
					self.stats['errorous'] += 1
				conn = None
				continue

			#check if 404
			with self.lock:
				if status == 404:
					#move
					folder = path['dst'][0:path['dst'].rindex('/')]
					if not os.path.exists(folder):
						os.makedirs(folder)
					renamed = False
					attempts = 0
					while not renamed and attempts < 100:
						try:
							os.rename(path['src'], path['dst'])
							renamed = True
						except:
							path['dst'] += 'x'
							renamed = False
							attempts += 1
					if not renamed:
						self.stats['errorous'] += 1
					else:
						self.stats['moved'] += 1
				else:
					#touch
					os.utime(path['src'], None)
					self.stats['touched'] += 1

		self.status = 0

	def populateFiles(self, src, dst):
		dirs = [src]
		while dirs:
			dir = dirs.pop()
			for file in os.listdir(dir):
				pathSrc = dir + '/' + file
				if not os.path.isfile(pathSrc):
					dirs.append(pathSrc)
				else:
					pathDst = dst + dir[len(src):] + '/' + file
					pathHost = pathSrc[len(src)+1:]
					pathUrl = ''
					if '/' in pathHost:
						pathUrl = pathHost[pathHost.find('/'):]
						pathHost = pathHost[0:pathHost.find('/')]
					paths.append({'src' : pathSrc, 'dst' : pathDst, 'url' : pathUrl, 'host' : pathHost})
					self.stats['max'] += 1

if __name__ == '__main__':
	main(sys.argv[1], sys.argv[2])
