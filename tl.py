#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import json
import http.client
from urllib.parse import urlencode
from urllib.parse import urlparse
from lib.colors import colorize

def get_language(code):
	synonyms = {"auto":["auto","detect"],"af":["af","afrikaans"],"sq":["sq","albanian"],"ar":["ar","arabic"],"hy":["hy","armenian"],"az":["az","azerbaijani"],"eu":["eu","basque"],"be":["be","belarusian"],"bn":["bn","bengali"],"bg":["bg","bulgarian"],"ca":["ca","catalan"],"zh-CN":["cn","zh-cn","china","chinese"],"hr":["hr","croatian"],"cs":["cs","cz","czech"],"da":["da","danish"],"nl":["nl","dutch"],"en":["en","eng","english"],"et":["et","est","estonian"],"tl":["tl","filipino"],"fi":["fi","finnish"],"fr":["fr","french"],"gl":["gl","galician"],"ka":["ka","georgian"],"de":["de","german"],"el":["el","greek"],"gu":["gu","gujarati"],"ht":["ht","haitian","creole"],"iw":["iw","hebrew"],"hi":["hi","hindi"],"hu":["hu","hungarian"],"is":["is","icelandic"],"id":["id","indonesian"],"ga":["ga","irish"],"it":["it","italian"],"ja":["ja","jp","jap","japanese"],"kn":["kn","kannada"],"ko":["ko","korean"],"la":["la","latin"],"lv":["lv","latvian"],"lt":["lt","lithuanian"],"mk":["mk","macedonian"],"ms":["ms","malay"],"mt":["mt","maltese"],"no":["no","norwegian"],"fa":["fa","persian"],"pl":["pl","pol","polish"],"pt":["pt","portuguese"],"ro":["ro","romanian"],"ru":["ru","russian"],"sr":["sr","serbian"],"sk":["sk","slovak"],"sl":["sl","slovenian"],"es":["es","spanish"],"sw":["sw","swahili"],"sv":["sv","swedish"],"ta":["ta","tamil"],"te":["te","telugu"],"th":["th","thai"],"tr":["tr","turkish"],"uk":["uk","ukrainian"],"ur":["ur","urdu"],"vi":["vi","vietnamese"],"cy":["cy","welsh"],"yi":["yi","yiddish"]}
	for (key, val) in list(synonyms.items()):
		if code in val:
			return key
	raise ValueError('Unknown language: {0}'.format(code))

if len(sys.argv) < 4:
	print('Too few arguments. Usage:', file=sys.stderr)
	print('{0} sourceLanguage destinationLanguage "text to translate" "text to translate 2"'.format(sys.argv[0]), file=sys.stderr)
	print('Example: {0} english japanese "Good morning"'.format(sys.argv[0]), file=sys.stderr)
	sys.exit(1)

try:
	langSrc = get_language(sys.argv[1].lower())
	langDest = get_language(sys.argv[2].lower())
except ValueError as e:
	print(e, file=sys.stderr)
	sys.exit(1)

for text in sys.argv[3:]:
	print('Translating "{0}":'.format(text))
	data = {'sl': langSrc, 'tl': langDest, 'text': text, 'client': 1}

	try:
		url = 'http://translate.google.com/translate_a/t?{0}'.format(urlencode(data))
		host = urlparse(url).netloc
		headers = { 'User-Agent': r'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.2.16) Gecko/20110319 Firefox/3.6.1' }
		client = http.client.HTTPConnection(host, timeout=3)
		client.request('GET', url, headers=headers)
		response = client.getresponse()
		encoding = response.headers.get_content_charset()
		content = response.read().decode(encoding)
	except Exception as e:
		print('error:', e, file=sys.stderr)
		sys.exit(1)

	data = json.loads(content)
	for sentence in data['sentences']:
		print('  ', end=' ')
		print(colorize(sentence['trans'], ['Fore.RED', 'Style.BRIGHT']), end=' ')
		print(colorize('(Transliteration: {0})'.format(sentence['translit']), ['Fore.WHITE', 'Style.DIM']) if 'translit' in sentence and sentence['translit'] else '')

	if 'dict' in data:
		for dict in sorted(data['dict'], key = lambda x: len(x['entry'])):
			print()
			print('Dictionary ({0}):'.format(dict['pos']) if 'pos' in dict and dict['pos'] else 'Dictionary:')
			for entry in dict['entry']:
				print('  ', end=' ')
				print(colorize(entry['word'], ['Fore.RED']), end=' ')
				print(colorize('(Reverse translation: {0})'.format(', '.join(entry['reverse_translation'])), ['Fore.WHITE', 'Style.DIM']) if 'reverse_translation' in entry and entry['reverse_translation'] else '')
	print()
