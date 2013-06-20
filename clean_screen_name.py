#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import re
import unittest

def clean_movie_name(x):
	# special characters
	x = x.replace('(', '[')
	x = x.replace(')', ']')
	for c in list('&-,;~ .'):
		x = x.replace(c, '_')

	# remove technical release info
	x = re.sub(r'x264|h264|h_264|xvid|divx|avc|flac|aac|sub|ac3|mp3|hi10p|10_?bit|8_?bit', '', x, flags=re.I)
	x = re.sub(r'dvdrip|dvd|hdtv|_bd|bd_|bdrip|blu_ray|bluray|web', '', x, flags=re.I)
	x = re.sub(r'2[0-9]_?[0-9]{,3}_?fps', '', x, flags=re.I)
	x = re.sub(r'dts|hdmi', '', x, flags=re.I)
	x = re.sub(r'5_1ch|5_1', '', x, flags=re.I)
	x = re.sub(r'480p|540p|720p|1080p|\d{3,}x\d{3,}', '', x, flags=re.I)
	x = re.sub(r'anamorphic', '', x, flags=re.I)

	# remove additional release info
	x = re.sub(r'v[2-9]', '', x, flags=re.I)
	x = re.sub(r'([0-9]{1,})v[0-9]', '\\1', x, flags=re.I)
	x = re.sub(r'fixed$', '', x, flags=re.I)
	x = re.sub(r'_end_', '', x, flags=re.I)
	# episode number
	x = re.sub(r'_ep(isode)?_*(\d+)', '_\\2', x, flags=re.I)
	# crc and default groups
	x = re.sub(r'\[\w{1,26}\]', '', x)

	# specific titles
	x = re.sub(r'Ore_no_Imouto_ga_Konna_ni_Kawaii_Wake_ga_Nai', 'Oreimo', x, flags=re.I)

	# specific groups with no brackets
	x = re.sub(r'_commie', '', x, flags=re.I)
	x = re.sub(r'steins_sub', '', x, flags=re.I)
	x = re.sub(r'a_f_k_', '', x, flags=re.I)
	x = re.sub(r'thora', '', x, flags=re.I)

	# final fixes
	x = re.sub(r'\]_*\[', '', x)
	x = re.sub(r'\[_*\]', '', x)
	x = re.sub(r'__+', '_', x)
	x = x.strip('_')
	return x


def clean(x):
	result = re.match(
		r'^(.*)\.' + \
		'(mkv|avi|mp4|mov|ogm|flv)' + \
		'_snapshot_' + \
		'([0-9.]+)_' + \
		'\[([0-9._]+)\]' + \
		'(\w*)' + \
		'\.(jpg|jpeg|png|jfif|gif)$', x, flags=re.I)
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
		}

		for source, expected in assertions.iteritems():
			actual = clean_movie_name(source)
			self.assertEqual(actual, expected)


if __name__ == '__main__':
	if len(sys.argv) == 1:
		print >>sys.stderr, 'No argument specified'
		sys.exit(1)
	if '--test' in sys.argv:
		suite = unittest.TestLoader().loadTestsFromTestCase(MainTest)
		unittest.TextTestRunner().run(suite)
		sys.exit(0)
	for x in sys.argv[1:]:
		print clean(x)
