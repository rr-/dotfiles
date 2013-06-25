try:
	import colorama
	colorama.init()
	available = True
except ImportError:
	available = False

def mkcolor(attrs = None):
	if not available:
		return ''
	if attrs is not None:
		a = ''
		for attr in attrs:
			(member1, member2) = attr.split('.')
			a += getattr(getattr(colorama, member1), member2)
		return a
	return reset()

def reset():
	if not available:
		return ''
	return colorama.Fore.RESET + colorama.Back.RESET + colorama.Style.RESET_ALL

def colorize(text, attrs):
	return mkcolor(attrs) + str(text) + reset()
