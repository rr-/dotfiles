#!/bin/bash
if [ -z "$1" ]; then
	echo No input file. 1>&2
	exit 1
fi

ffmpeg=$(command -v ffmpeg)
if [ -z "$ffmpeg" ]; then
	list=( /cygdrive/z/software/utilities/*ffmpeg*/bin/ffmpeg.exe )
	ffmpeg="${list[0]}"
fi

if [ -z "$ffmpeg" ]; then
	echo ffmpeg not found. 1>&2
	exit 1
fi

in="$1"
out="$(echo $1|sed 's/gif/webm/i')"

"$ffmpeg" -i "$in" -c:v libvpx -crf 12 -b:v 500K "$out"
