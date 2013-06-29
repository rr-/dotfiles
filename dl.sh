#!/bin/bash
[ "$#" -ne 4 ] && echo "Usage: $0 dst_dir first_url accept_regex completed_list_file" && exit 1
completed_file="$4"
dst_dir="$1"
first_url="$2"
accept="$3"

tmp_dir=$(mktemp -d)
queue_file="$tmp_dir/queue.lst"
content_file="$tmp_dir/dl_content.dat"
headers_file="$tmp_dir/dl_headers.dat"
sess_completed_file="$tmp_dir/completed.lst"

addurl () {
	if ! grep -Fxq "$1" "$completed_file"; then
		if ! grep -Fxq "$1" "$sess_completed_file"; then
			echo "$1" >>"$queue_file"
		fi
	fi
}
onexit () {
	rm -rf "$tmp_dir"
	exit 1
}
atomic () {
	if [ "$atomic" == 1 ]; then
		atomic=0
		trap "exit 1" SIGINT
	else
		atomic=1
		trap "" SIGINT
	fi
}

trap onexit EXIT
touch "$completed_file"
touch "$sess_completed_file"
addurl "$first_url"

while true; do
	if ! read url <"$queue_file"; then
		break
	fi

	echo -n "Downloading $url... "

	wget "$url" -kqSO "$content_file" 2>"$headers_file"

	#a website
	if grep -qi 'Content-Type:\s*text/html' "$headers_file"; then
		echo "adding links"
		grep -oP "http:\/\/[^'\"#<>]*" "$content_file"|sort|uniq|grep -P "$accept"|while read suburl; do
			addurl "$suburl"
		done
		echo "$url">>"$sess_completed_file"
	#an image
	elif grep -qi 'Content-Type:\s*image/' "$headers_file"; then
		echo "saving"
		dst_path="$dst_dir"/"$(echo -n ${url##*://}|sed 's/[^a-zA-Z0-9\/\.-]/_/')"
		mkdir -p "$(dirname "$dst_path")"
		mv "$content_file" "$dst_path"
		echo "$url">>"$completed_file"
	fi

	atomic
	tail "$queue_file" -n +2|sort|uniq > "$queue_file~"
	mv "$queue_file~" "$queue_file"
	atomic
done
