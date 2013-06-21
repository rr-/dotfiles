#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import sys
import subprocess
from lib.proc import execute

def make_backup(file):
	backup = file + '~'
	if os.path.exists(backup):
		raise Exception('%s already exists' % backup)
	os.rename(file, backup)
	return backup, file

def transfer_stat(src, dst):
	atime = os.path.getatime(src) #this is changed immediately after rename
	mtime = os.path.getmtime(src)
	os.utime(dst, (atime, mtime))

class Operation(object):
	def run_all(self, files):
		for file in files:
			try:
				if not os.path.exists(file):
					raise Exception('%s does not exist' % file)
				elif not os.path.isfile(file):
					raise Exception('%s is not a file' % file)
				else:
					self.run(file)
			except Exception as e:
				print >>sys.stderr, str(e)


class DegradeOperation(Operation):
	name = ['degrade', 'downgrade']

	def run(self, file):
		backup, file = make_backup(file)
		new = os.path.splitext(file)[0] + '.jpg'
		cmd  = ['convert']
		cmd += ['%s[0]' % backup]
		cmd += ['-quality', '80']
		cmd += ['jpg:%s' % new]
		execute(cmd)
		transfer_stat(backup, file)


class FixAnamorphicOperation(Operation):
	name = ['fix-anamorphic']

	def run(self, file):
		cmd  = ['identify']
		cmd += ['-format', '%w %h']
		cmd += ['%s[0]' % file]
		out = execute(cmd)[1]
		w, h = map(int, out.split(' '))
		nw = h * 16 // 9
		nh = h
		backup, file = make_backup(file)
		cmd  = ['convert']
		cmd += ['%s[0]' % backup]
		cmd += ['-resize', '%dx%d!' % (nw, nh)]
		cmd += [file]
		execute(cmd)
		transfer_stat(backup, file)


class FixPngOperation(Operation):
	name = ['fix-png']

	def run(self, file):
		_, extension = os.path.splitext(file)
		if extension.lower() != '.png':
			raise Exception('%s is not a PNG file' % file)
		cmd  = ['identify']
		cmd += ['-format', '%r']
		cmd += [file]
		out = execute(cmd)[1]
		if out.strip() == 'PseudoClassGrayMatte':
			cmd  = ['convert']
			cmd += [file]
			cmd += ['-alpha', 'off']
			cmd += [file]
			execute(cmd)


class StitchOperation(Operation):
	name = ['stitch']

	def run_all(self, files):
		output = 'stitched.jpg'
		cmd  = ['convert']
		cmd += ['-border', '0x1']
		cmd += ['-bordercolor', 'black']
		cmd += files
		cmd += ['-append', '-trim']
		cmd += [output]
		execute(cmd)



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
