#!/usr/bin/perl
foreach $s(@ARGV)
{
	($_, $mext, $lts, $sts, $info, $sext) = $s =~ m/(.*)\.(mkv|avi|mp4|mov|ogm|flv)_snapshot_([0-9.]+)_\[([0-9._]+)\]([\[a-zA-Z0-9\]]*)\.(jpg|jpeg|png|jfif|gif)$/i;
	print $s and next if !$_;
	$sts =~ s/\.//g;
	$sts =~ s/_/-/g;
	#special characters
	s/&/_/g;
	s/-/_/g;
	s/,/_/g;
	s/;/_/g;
	s/~/_/g;
	s/ /_/g;
	s/\./_/g;
	s/\'/`/g;

	# remove technical release info
	s/x264|h264|h.264|xvid|divx|avc|flac|aac|ac3|mp3//gi;
	s/dvdrip|dvd|hdtv|_bd|bd_|bdrip|blu_ray|bluray//gi;
	s/2[0-9.]+_?fps//gi;
	s/dts|hd_?ma//gi;
	s/5_1ch|5_1//gi;
	s/480p|540p|720p|1080p|\x{3,}x\d{3,}//gi;
	s/anamorphic//gi;

	# remove additional release info
	s/v[2-9]//gi;
	s/fixed$//gi;

	# group-specific
	s/_commie//gi;
	s/steins_sub//gi;
	s/a\.f\.k\.//gi;
	s/thora//gi;
	s/\[[0-9a-zA-Z_]{1,16}\]//g; #[group name], [crc]
	s/\([0-9a-zA-Z_]{1,16}\)//g; #(group name), (crc)

	# anime-specific
	s/mahou_shoujo_lyrical//gi;
	s/magical_girl_lyrical//gi;
	s/mahou_shoujo_madoka/Madoka/gi;
	s/magical_girl_madoka/Madoka/gi;
	s/ore_no_imouto_ga_konna_ni_kawaii_wake_ga_nai/Oreimo/gi;

	# fix character sequences that could stack
	s/\]\[//g;
	s/\)\(//g;

	#episode
	s/_ep(isode)?_?(\d+)/_$2/gi;


	# final fixes
	s/\[\]//g;
	s/\(\)//g;
	s/\(_//g;
	s/_\)//g;
	s/\[_//g;
	s/_\]//g;
	s/__+/_/g;
	s/^_+//g;
	s/_+$//g;

	print $_ . "[$lts][$sts]$info.$sext";
}