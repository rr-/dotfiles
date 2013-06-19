#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import sys
import subprocess

class Operation(object):
	def run_all(self, files):
		for file in files:
			try:
				if not os.path.exists(file):
					raise Exception(file + ' does not exist')
				elif not os.path.isfile(file):
					raise Exception(file + ' is not a file')
				else:
					self.run(file)
			except Exception as e:
				print >>sys.stderr, str(e)

	def backup(self, file):
		backup = file + '~'
		if os.path.exists(backup):
			raise Exception(backup + ' already exists')
		os.rename(file, backup)
		return backup, file

	def transferFileStats(self, src, dst):
		atime = os.path.getmtime(src)
		mtime = os.path.getmtime(src)
		os.utime(dst, (atime, mtime))

	def call(self, cmd):
		proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
		out = proc.communicate()[0]
		return out



class DegradeOperation(Operation):
	name = ['degrade', 'downgrade']

	def run(self, file):
		backup, file = self.backup(file)
		new = os.path.splitext(file)[0] + '.jpg'
		cmd = [
			'convert',
			'%s[0]' % backup,
			'-quality', '80',
			'jpg:' + new]
		self.call(cmd)
		self.transferFileStats(backup, file)


class FixAnamorphicOperation(Operation):
	name = ['fix-anamorphic']

	def run(self, file):
		cmd = [
			'identify',
			'-format', '%w %h',
			file + '[0]']
		out = self.call(cmd)
		w, h = map(int, out.split(' '))
		nw = h * 16 // 9
		nh = h
		backup, file = self.backup(file)
		cmd = ['convert',
			'%s[0]' % backup,
			'-resize', '%dx%d!' % (nw, nh),
			file]
		self.call(cmd)
		self.transferFileStats(backup, file)


class FixPngOperation(Operation):
	name = ['fix-png']

	def run(self, file):
		_, extension = os.path.splitext(file)
		if extension.lower() != '.png':
			raise Exception(file + ' is not a PNG file')
		cmd = ['identify',
			'-format', '%r',
			file]
		out = self.call(cmd)
		if out.strip() == 'PseudoClassGrayMatte':
			cmd = ['convert',
				file,
				'-alpha', 'off',
				file]
			subprocess.call(cmd)


if __name__ == '__main__':
	if len(sys.argv) < 3:
		print >>sys.stderr, 'Too few arguments.'
		sys.exit(1)

	op_name = sys.argv[1]
	files = sys.argv[2:]

	for operation in Operation.__subclasses__():
		if op_name in operation.name:
			op = operation()
			op.run_all(files)
			sys.exit(0)

	print >>sys.stderr, 'Unknown argument:', sys.argv[1]
	sys.exit(1)
