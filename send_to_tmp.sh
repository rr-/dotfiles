#!/bin/bash
. config.ini
src_folder=/cygdrive/z/hub/tmp/queued/
done_folder=/cygdrive/z/hub/tmp/done/
dst_folder=/srv/www/tmp.sakuya.pl/public_html/f/
base_url=http://tmp.sakuya.pl/f/

mkdir -p $src_folder
mkdir -p $done_folder

for file in "$@"; do
	if [ ! -f "$file" ]; then
		echo "$file not found" 2>&1
	else
		cp "$file" "$src_folder"
	fi
done

ssh -n "$user@$server_addr" "mkdir -p \"$dst_folder\"; chmod 0755 \"$dst_folder\""
i=0
find "$src_folder" -type f|while read line; do
	src_path="$line"
	dst_path="$dst_folder"${src_path##*/}

	src_quoted=$(echo "$src_path"|sed 's/[ ()]/\0/g;')
	dst_quoted=$(echo "$dst_path"|sed 's/[ ()]/\\\0/g;')
	scp -q "$src_quoted" "$user@$server_addr:$dst_quoted"
	ssh -n "$user@$server_addr" "touch \"$dst_path\" -d \"$ts\"; chmod 0644 \"$dst_path\""

	echo "${base_url}${src_path##*/}"

	mv "$src_path" "$done_folder"
done
