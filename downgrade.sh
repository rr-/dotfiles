#!/bin/bash
[ -z "$@" ] && echo "No files selected" && exit 1
for p in "$@"
do
	echo "$p"
	pb="$p~"
	p2=`echo "$p"|sed 's/\.[^\.]*$/.jpg/'`
	mv "$p" "$pb" || exit 1
	convert "$pb" -quality 80 jpg:"$p2" || exit 1
done
