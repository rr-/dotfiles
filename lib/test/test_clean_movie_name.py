#!/usr/bin/python
# -*- coding: utf-8 -*-
import unittest
import lib.string

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
			actual = lib.string.clean_movie_name(source)
			self.assertEqual(actual, expected)

if __name__ == "__main__":
	unittest.main()
