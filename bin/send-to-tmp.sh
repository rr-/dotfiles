#!/bin/bash

dst_folder=/srv/www/tmp.sakuya.pl/public_html/f/
base_url=http://tmp.sakuya.pl/f/
remote_user=rr-
remote_addr=tmp.sakuya.pl
remote_port=65000

ssh -p"$remote_port" -n "$remote_user@$remote_addr" "mkdir -p \"$dst_folder\"; chmod 0755 \"$dst_folder\""

for src_path in "$@"; do
	if [ ! -e "$src_path" ]; then
		echo "$src_path not found" 2>&1
	else
		fragment=$(basename "$src_path")
		dst_path="$dst_folder$fragment"

		src_quoted=$(echo "$src_path"|sed 's/[ ()]/\0/g;')
		dst_quoted=$(echo "$dst_path"|sed 's/[ ()]/\\\0/g;')

		scp -r -P"$remote_port" -q "$src_quoted" "$remote_user@$remote_addr:$dst_quoted"

		if [ -d "$src_path" ]; then
			chmod=0755
		elif [ -f "$src_path" ]; then
			chmod=0644
		fi

		ssh -p"$remote_port" -n "$remote_user@$remote_addr" "touch \"$dst_path\"; chmod $chmod \"$dst_path\""

		echo "$base_url$fragment"
	fi
done
