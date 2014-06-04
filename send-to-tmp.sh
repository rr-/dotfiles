#!/bin/bash

dst_folder=/srv/www/tmp.sakuya.pl/public_html/f/
base_url=http://tmp.sakuya.pl/f/
remote_user=rr-
remote_addr=tmp.sakuya.pl
remote_port=65000

ssh -p"$remote_port" -n "$remote_user@$remote_addr" "mkdir -p \"$dst_folder\"; chmod 0755 \"$dst_folder\""

for src_path in "$@"; do
	if [ ! -f "$src_path" ]; then
		echo "$src_path not found" 2>&1
	else
		dst_path="$dst_folder"${src_path##*/}

		src_quoted=$(echo "$src_path"|sed 's/[ ()]/\0/g;')
		dst_quoted=$(echo "$dst_path"|sed 's/[ ()]/\\\0/g;')

		scp -P"$remote_port" -q "$src_quoted" "$remote_user@$remote_addr:$dst_quoted"
		ssh -p"$remote_port" -n "$remote_user@$remote_addr" "touch \"$dst_path\"; chmod 0644 \"$dst_path\""

		echo "${base_url}${src_path##*/}"
	fi
done
