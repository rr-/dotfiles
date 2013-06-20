#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import sys
import subprocess

def backup(file):
	backup = file + '~'
	if os.path.exists(backup):
		raise Exception(backup + ' already exists')
	os.rename(file, backup)
	return backup, file

def transferFileStats(src, dst):
	atime = os.path.getatime(src) #this is changed immediately after rename
	mtime = os.path.getmtime(src)
	os.utime(dst, (atime, mtime))

def call(cmd):
	proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
	out = proc.communicate()[0]
	return out


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


class DegradeOperation(Operation):
	name = ['degrade', 'downgrade']

	def run(self, file):
		backup, file = makeBackup(file)
		new = os.path.splitext(file)[0] + '.jpg'
		cmd  = ['convert']
		cmd += ['%s[0]' % backup]
		cmd += ['-quality', '80']
		cmd += ['jpg:' + new]
		call(cmd)
		transferFileStats(backup, file)


class FixAnamorphicOperation(Operation):
	name = ['fix-anamorphic']

	def run(self, file):
		cmd  = ['identify']
		cmd += ['-format', '%w %h']
		cmd += [file + '[0]']
		out = call(cmd)
		w, h = map(int, out.split(' '))
		nw = h * 16 // 9
		nh = h
		backup, file = makeBackup(file)
		cmd  = ['convert']
		cmd += ['%s[0]' % backup]
		cmd += ['-resize', '%dx%d!' % (nw, nh)]
		cmd += [file]
		call(cmd)
		transferFileStats(backup, file)


class FixPngOperation(Operation):
	name = ['fix-png']

	def run(self, file):
		_, extension = os.path.splitext(file)
		if extension.lower() != '.png':
			raise Exception(file + ' is not a PNG file')
		cmd  = ['identify']
		cmd += ['-format', '%r']
		cmd += [file]
		out = call(cmd)
		if out.strip() == 'PseudoClassGrayMatte':
			cmd  = ['convert']
			cmd += [file]
			cmd += ['-alpha', 'off']
			cmd += [file]
			call(cmd)



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
