#!/usr/bin/python
import subprocess, threading
import os, tempfile
import time
import urllib
import datetime

commonArgs = \
{
	'year': datetime.date.today().year,
	'month': datetime.date.today().month,
}

#settings
user = 'rr-'
host = '192.168.1.4'
sourceFolder = "/cygdrive/z/hub/pinkyard/queued/"
safeFolder = '/cygdrive/z/hub/pinkyard/done/'
destFolder = '/srv/www/pinkyard/public_html/files/{year:04d}-{month:02d}'.format(**commonArgs)
clipUrl = 'http://pink.sakuya.pl/resolve/{year:04d}-{month:02d}/{urlName:s}'

class dotdict(dict):
	def __getattr__(self, attr):
		return self.get(attr, None)
	__setattr__= dict.__setitem__
	__delattr__= dict.__delitem__

#normal command
def execute(commands):
	proc = subprocess.Popen(commands, stdout=subprocess.PIPE)
	(out, err) = proc.communicate()
	return (proc.returncode, out, err)

#prepare commands
commands = []
y = ''
for x in destFolder.strip('/').split('/'):
	y += '/' + x
	commands.append('-mkdir "{0}"'.format(y))

files = []
for name in os.listdir(sourceFolder):
	file = dotdict()
	file.sourceFolder = sourceFolder
	file.sourceName = name
	file.sourcePath = os.path.join(sourceFolder, name)
	if not os.path.isfile(file.sourcePath):
		continue
	file.destName = execute(['clean-screen-name.pl', name])[1]
	file.urlName = urllib.quote(file.destName)
	file.time = os.stat(file.sourcePath).st_atime
	args = dict(file.items() + commonArgs.items())
	file.destFolder = destFolder
	file.safePath = os.path.join(safeFolder.format(**args), name)
	files.append(file)
if len(files) == 0:
	os.sys.exit(0)

i = 0
for file in sorted(files, key=lambda f: f['time']):
	future = time.mktime((datetime.datetime.now() + datetime.timedelta(seconds=i)).timetuple())
	os.utime(file.sourcePath, (future, future))
	i += 1
	commands.append('put -p "{sourceFolder}/{sourceName}" "{destFolder}/{destName}"'.format(**file))
	commands.append('chmod 0744 "{destFolder}/{destName}"'.format(**file))

#os.sys.exit(1)
#write file, execute sftp
commandListFile = tempfile.TemporaryFile()
commandListFile.write("\n".join(commands))
commandListFile.flush()

result = execute(['sftp', '-b', commandListFile.name, user + '@' + host])
print >>os.sys.stderr, result[1]
commandListFile.close()

if result[0] == 0:
	clip = ''
	for file in files:
		try:
			os.rename (file.sourcePath, file.safePath)
		except:
			print >>os.sys.stderr, 'Error', file.sourcePath, file.safePath
		args = dict(commonArgs.items() + file.items())
		print execute(['wget', '-qO-', clipUrl.format(**args)])[1]
