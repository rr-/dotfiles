import subprocess

def execute(cmd):
	proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
	out, err = proc.communicate()
	return (proc.returncode, out, err)
