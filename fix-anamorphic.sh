#!/bin/sh
[ -z "$@" ] && echo "No files selected" && exit 1
for p in "$@"
do
	w=$(identify -format "%w" "$p")
	h=$(identify -format "%h" "$p")
	nw=$(( $h * 16 / 9 ))
	nh=$h
	echo "$p ${w}x${h} -> ${nw}x${nh}"
	convert "$p" -resize "${nw}x${nh}!" "$p.tmp" || exit 1
	mv "$p" "$p~" || exit 1
	mv "$p.tmp" "$p" || exit 1
	touch -m --date "$(stat "$p~" --format '%y')" "$p"
done