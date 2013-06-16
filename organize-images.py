#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import re
import time
import threading
import subprocess
from PIL import Image

src_rsync = 'rr-@burza:/home/rr-/img/dead/'
src_dir = '/cygdrive/z/img/net/unfiltered'
dst_dir = '/cygdrive/z/img/net/filtered'
min_width = 400
min_height = 400
max_files = 1000

stats = \
{
	'processed': 0,
	'removed': 0,
	'moved': 0
}


class Worker(threading.Thread):
	def __init__(self, src_dir, dst_dir, min_width, min_height, max_files):
		threading.Thread.__init__(self)
		self.src_dir = src_dir
		self.dst_dir = dst_dir
		self.min_width = min_width
		self.min_height = min_height
		self.max_files = max_files
		self.kill_received = False

	def get_dst_dir(self, dir, subdir_number = None):
		#prepare destination directory
		dst_dir_base = self.dst_dir + dir[len(self.src_dir):]
		dst_dir_base = re.sub(r'/[^/]*\.2chan\.net', r'/2chan', dst_dir_base)
		dst_dir_base = re.sub(r'/images\.4chan\.org', r'/4chan', dst_dir_base)
		dst_dir_base = re.sub(r'/src', '', dst_dir_base)
		#get last (or next) subdir is available
		file_counter = 0
		if subdir_number is None and os.path.exists(dst_dir_base):
			dst_dir = None
			for file in os.listdir(dst_dir_base):
				if re.match(r'^\d{3}$', file) and int(file) > subdir_number:
					subdir_number = int(file)
					dst_dir = os.path.join(dst_dir_base, '%03d' % subdir_number)
			if dst_dir is not None:
				file_counter = len(os.listdir(dst_dir))
				if file_counter >= max_files:
					subdir_number += 1
		#not specified in param, no folder found, or no subdir found
		if subdir_number is None:
			subdir_number = 1
		dst_dir = os.path.join(dst_dir_base, '%03d' % subdir_number)
		#return dir info along with file counter
		return (dst_dir, subdir_number, file_counter)

	def run(self):
		print >>sys.stderr, 'Working...'
		dirs = [self.src_dir]
		dirs_final = []
		while not self.kill_received and len(dirs) > 0:
			dir = dirs.pop()
			dirs_final.append(dir)
			(dst_dir, subdir_number, file_counter) = self.get_dst_dir(dir)

			try:
				files = os.listdir(dir)
			except:
				continue

			for file in files:
				if self.kill_received:
					break

				path = os.path.join(dir, file)

				if os.path.isdir(path):
					dirs.append(path)
					continue

				stats['processed'] += 1
				print path,

				shouldRemove = False
				try:
					img = Image.open(path)
					width, height = img.size
					if width * height < 500*500:
						if img.format != 'GIF':
							if re.search('(2chan|4chan)', dst_dir):
								shouldRemove = True
								print '%dx%d < %dx%d' % (width, height, min_width, min_height)
				except:
					pass

				if shouldRemove:
					stats['removed'] += 1
					os.unlink(path)
				else:
					if file_counter >= max_files:
						(dst_dir, subdir_number, file_counter) = self.get_dst_dir(dir, subdir_number + 1)
					if not os.path.exists(dst_dir):
						os.makedirs(dst_dir)
						pass

					dst_path = os.path.join(dst_dir, os.path.basename(path))
					print 'moving to %s' % dst_path
					os.rename(path, dst_path)
					stats['moved'] += 1
					file_counter += 1

		while not self.kill_received and len(dirs_final) > 0:
			dir = dirs_final.pop()
			if os.path.exists(dir) and dir != self.src_dir:
				os.rmdir(dir)

		print >>sys.stderr, 'Done'
		print >>sys.stderr, 'Files moved:     %d' % stats['moved']
		print >>sys.stderr, 'Files removed:   %d' % stats['removed']
		print >>sys.stderr, 'Files processed: %d' % stats['processed']

def main(args):
	cmd = 'rsync -avz --remove-source-files %s %s' % (src_rsync, src_dir)
	print cmd
	subprocess.call(cmd, shell=True)
	t = Worker(src_dir, dst_dir, min_width, min_height, max_files)
	t.start()
	try:
		t.join(1)
		while t.isAlive():
			time.sleep(1)
			pass
	except KeyboardInterrupt:
		print >>sys.stderr, 'Ctrl+C received.'
		t.kill_received = True

if __name__ == '__main__':
	main(sys.argv)
