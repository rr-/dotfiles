#!/bin/sh
if [ -z "$1" ]; then
	echo No input files. 1>&2
	exit 1
fi

for x in "$@"; do
	[ -f "$x" ] || continue

	echo "$x"

	#remove \r, BOM and strip trailing spaces
	sed 's/$//; 1 s/\xEF\xBB\xBF//; s/[	 ]*$//' -i "$x"

	#remove lines at beginning and end of file
	sed -e :a -e '/./,$!d;/^\n*$/{$d;N;};/\n$/ba' -i "$x"
done
