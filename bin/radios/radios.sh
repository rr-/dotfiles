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

playlist="radios.pls"
index=1

echo '[playlist]' > "$playlist"

while read -r line
do
    url=$(echo "$line"|sed 's/\s*;.*$//g')
    comment=$(echo "$line"|sed 's/^.*;//g')

    if [ -z $url ]; then
        continue
    fi

    echo "$url"
    if [[ "$url" == *.m3u || "$url" == *.pls ]]; then
        tmp_file=$(mktemp -u)
        wget "$url" --connect-timeout=1 --read-timeout=1 --tries=1 -qO- |\
        grep -o 'http://.*' >"$tmp_file"

        while read -r sub_url; do
            echo -e "\t$sub_url"
            echo "Title$index=$comment" >> "$playlist"
            echo "File$index=$sub_url" >> "$playlist"
            ((index++))
        done < "$tmp_file"

        rm "$tmp_file"
    else
        echo "Title$index=$comment" >> "$playlist"
        echo "File$index=$url" >> "$playlist"
        ((index++))
    fi
done < "radios.lst"

echo "Version=2" >> "$playlist"
echo "NumberOfEntries=$index" >> "$playlist"

"$foobar_path" "$playlist"
