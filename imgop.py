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



class DegradeOperation(Operation):
	name = ['degrade', 'downgrade']

	def run(self, file):
		backup, file = self.backup(file)
		new = os.path.splitext(file)[0] + '.jpg'
		args = []
		args += [backup + '[0]']
		args += ['-quality', '80']
		args += ['jpg:' + new]
		subprocess.call(['convert'] + args)



class FixAnamorphicOperation(Operation):
	name = ['fix-anamorphic']

	def run(self, file):
		args = []
		args += ['-format', '%w %h']
		args += [file + '[0]']
		proc = subprocess.Popen(['identify'] + args, stdout=subprocess.PIPE)
		w, h = map(int, proc.communicate()[0].split(' '))
		nw = h * 16 // 9
		nh = h
		backup, file = self.backup(file)
		args = []
		args += [backup]
		args += ['-resize', '%dx%d!' % (nw, nh)]
		args += [file]
		subprocess.call(['convert'] + args)




if __name__ == '__main__':
	if len(sys.argv) < 3:
		print >>sys.stderr, 'Too few arguments.'
		sys.exit(1)

	op_name = sys.argv[1]
	files = sys.argv[2:]

	for operation in Operation.__subclasses__():
		if op_name in list(operation.name):
			op = operation()
			op.run_all(files)
			sys.exit(0)

	print >>sys.stderr, 'Unknown argument:', sys.argv[1]
	sys.exit(1)
