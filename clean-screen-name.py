#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import re
import unittest

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


def clean_screencap_name(x):
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

class MainTest(unittest.TestCase):
	def test_clean_movie_name(self):
		assertions = {
			'[Hatsuyuki]_Kotoura-san_-_12_END_[10bit][1280x720][97E96800]': 'Kotoura_san_12',
			'[THISFILEHASNOSUBS] Chousoku Henkei Gyrozetter - 37 [28D7F025]': 'Chousoku_Henkei_Gyrozetter_37',
			'[Zero-Raws] Kidou Senshi Gundam Unicorn - 06 (BD 1920x1080 x264 FLAC)': 'Kidou_Senshi_Gundam_Unicorn_06',
			'[FFF] DATE A LIVE - 12v0 [97336508]': 'DATE_A_LIVE_12',
			'[ISLAND]One_Piece_600_[8bit-VFR]_[720p]_[BE755A1E]': 'One_Piece_600',
			'[SnI][Island-Fansub]Suisei_no_Gargantia_-_11_[8bit]_[480p]_[41166952]': 'Suisei_no_Gargantia_11',
			'[SnI][Island-Fansub]Suisei_no_Gargantia_-_11_[10bit]_[720p]_[CD820E1B]': 'Suisei_no_Gargantia_11',
			'[chuu-Raws] コロッケ！Croket! - 01 (WEB 640x480 Vorbis)': 'コロッケ！Croket!_01',
			'[Kamigami] Suisei no Gargantia - 11 [1280x720 x264 AAC Sub(Chs,Cht,Jap)]': 'Suisei_no_Gargantia_11',
			'[Kamigami] Ore no Imouto ga Konna ni Kawaii Wake ga Nai S2 - 11 [1280x720 x264 AAC Sub(Chi,Jap)]': 'Oreimo_S2_11',
			'[WhyNot] Uta no Prince-sama Maji Love 2000% - 12 [08627933]': 'Uta_no_Prince_sama_Maji_Love_2000%_12',
			'[DeadFish] Dansai Bunri no Crime Edge - 12 [720p][AAC]': 'Dansai_Bunri_no_Crime_Edge_12',
			'[Commie] Red Data Girl - 12 [B0D20687]': 'Red_Data_Girl_12',
			'[Mabushii] Saint Seiya Omega - 43 [WEB][134FE830]': 'Saint_Seiya_Omega_43',
			'[Anime-Koi] Dansai Bunri no Crime Edge - 12 [h264-720p][3098FF6E]': 'Dansai_Bunri_no_Crime_Edge_12',
			'[SFW] Queen\'s Blade Rebellion - A Saint\'s Agony ~ The Door of Faith Reopens [Hi10P][46EF7E6B]': 'Queen\'s_Blade_Rebellion_A_Saint\'s_Agony_The_Door_of_Faith_Reopens',
		}

		for source, expected in assertions.iteritems():
			actual = clean_movie_name(source)
			self.assertEqual(actual, expected)


if __name__ == '__main__':
	if len(sys.argv) == 1:
		print >>sys.stderr, 'No argument specified'
		sys.exit(1)
	elif '--test' in sys.argv:
		suite = unittest.TestLoader().loadTestsFromTestCase(MainTest)
		unittest.TextTestRunner().run(suite)
	else:
		for x in sys.argv[1:]:
			print clean_screencap_name(x)
