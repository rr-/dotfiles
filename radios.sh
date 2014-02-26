#!/bin/bash

function find_exe()
{
	exe="$1"
	shift
	for x in "$@"; do
		if [ -f "$x/$exe" ]; then
			echo "$x/$exe"
		fi
	done
}

foobar_path=$(find_exe foobar2000.exe \
	'C:/Program Files/foobar2000' \
	'C:/Program Files (x86)/foobar2000')

if [ -z "$foobar_path" ]; then
	echo Foobar not found! 1>&2
	exit 1
fi

cat "radios.lst" | sed '/^\s*$/d' | while read line; do
	url=$(echo "$line"|sed 's/\s*;.*$//g')
	"$foobar_path" /add "$url"
done
