#!/bin/bash
. config.ini
src_folder=/cygdrive/z/hub/pinkyard/queued/
done_folder=/cygdrive/z/hub/pinkyard/done/
dst_folder=/srv/www/pinkyard/public_html/files/$(date +'%Y-%m')/

ssh -n "$user@$server_addr" "mkdir -p \"$dst_folder\"; chmod 0755 \"$dst_folder\""
i=0
find "$src_folder" -type f -print0|xargs -r0 stat -c '%A %n'|sort|while read line; do
	src_file=$(echo "$line"|cut -f2- -d ' ')
	dst_file="$dst_folder"${src_file##*/}
	i=$[ $i + 1 ]
	ts=$(date -d "+$i seconds")
	resolver_url="http://pink.sakuya.pl/resolve/$(date +'%Y-%m')/"
	resolver_url+=$(echo -ne "${src_file##*/}"|xxd -plain|sed 's/\(..\)/%\1/g')

	src_quoted=$(echo "$src_file"|sed 's/[ ()]/\0/g;')
	dst_quoted=$(echo "$dst_file"|sed 's/[ ()]/\\\0/g;')
	scp -q "$src_quoted" "$user@$server_addr:$dst_quoted"
	ssh -n "$user@$server_addr" "touch \"$dst_file\" -d \"$ts\"; chmod 0644 \"$dst_file\""

	wget "$resolver_url" -qO -
	echo

	mv "$src_file" "$done_folder"
done
