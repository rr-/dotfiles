import re

def replace(pattern, replacement, subject):
	regex = re.compile(pattern, flags=re.IGNORECASE)
	return re.sub(regex, replacement, subject)

def clean_movie_name(x):
	# special characters
	x = x.replace('(', '[')
	x = x.replace(')', ']')
	for c in list('&-,;~ .'):
		x = x.replace(c, '_')

	# remove technical release info
	x = replace(r'x264|h264|h_264|xvid|divx|avc|flac|aac|sub|ac3|mp3|hi10p|10_?bit|8_?bit', '', x)
	x = replace(r'dvdrip|dvd|hdtv|_bd|bd_|bdrip|blu_ray|bluray|web', '', x)
	x = replace(r'2[0-9]_?[0-9]{,3}_?fps', '', x)
	x = replace(r'dts|hdmi', '', x)
	x = replace(r'5_1ch|5_1', '', x)
	x = replace(r'480p|540p|720p|1080p|\d{3,}x\d{3,}', '', x)
	x = replace(r'anamorphic', '', x)

	# remove additional release info
	x = replace(r'v[2-9]', '', x)
	x = replace(r'([0-9]{1,})v[0-9]', '\\1', x)
	x = replace(r'fixed$', '', x)
	x = replace(r'_end_', '', x)
	# episode number
	x = replace(r'_ep(isode)?_*(\d+)', '_\\2', x)
	# crc and default groups
	x = replace(r'\[\w{1,26}\]', '', x)

	# specific titles
	x = replace(r'Ore_no_Imouto_ga_Konna_ni_Kawaii_Wake_ga_Nai', 'Oreimo', x)

	# specific groups with no brackets
	x = replace(r'_commie', '', x)
	x = replace(r'steins_sub', '', x)
	x = replace(r'a_f_k_', '', x)
	x = replace(r'thora', '', x)

	# final fixes
	x = replace(r'\]_*\[', '', x)
	x = replace(r'\[_*\]', '', x)
	x = replace(r'__+', '_', x)
	x = x.strip('_')
	return x

def clean_screen_name(x):
	result = re.match(
		r'^(.*)\.' + \
		'(mkv|avi|mp4|mov|ogm|flv)' + \
		'_snapshot_' + \
		'([0-9.]+)_' + \
		'\[([0-9._]+)\]' + \
		'(\w*)' + \
		'\.(jpg|jpeg|png|jfif|gif)$', x)
	if not result:
		return x
	mname, mext, mts, sts, extra, sext = result.groups()

	return '%s[%s][%s]%s.%s' % (
		clean_movie_name(mname),
		mts,
		sts.replace('.', '').replace('_', '-'),
		extra,
		sext)
