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

onexit () {
	rm -rf "$tmp_dir"
	exit 0
}
atomic () {
	[ "$atomic" == 1 ] \
		&& { atomic=0; trap "exit 1" SIGINT; } \
		|| { atomic=1; trap "" SIGINT; }
}

trap onexit EXIT
touch "$completed_file"
touch "$sess_completed_file"
echo "$first_url" >>"$queue_file"

while true; do
	if ! read url <"$queue_file"; then
		break
	fi

	echo -n "Downloading $url... "
	wget "$url" -kqSO "$content_file" 2>"$headers_file"
	[ $? -ne 0 ] && echo "error" && exit 1

	#a website
	if grep -qi 'Content-Type:\s*text/html' "$headers_file"; then
		echo "adding links"
		grep -oP "http:\/\/[^'\"#<>]*" "$content_file"|sort|uniq|grep -P "$accept"|while read suburl; do
			echo "$suburl" >>"$queue_file"
		done
		echo "$url">>"$sess_completed_file"
	#an image
	elif grep -qi 'Content-Type:\s*image/' "$headers_file"; then
		echo "saving"
		dst_path="$dst_dir"/"$(echo -n ${url##*://}|sed 's/[^a-zA-Z0-9\/\.-]/_/')"
		mkdir -p "$(dirname "$dst_path")"
		mv "$content_file" "$dst_path"
		echo "$url">>"$completed_file"
	else
		echo "ignoring"
	fi

	atomic
	tail "$queue_file" -n +2|sort|uniq|grep -Fxv -f "$completed_file" -f "$sess_completed_file" > "$queue_file~"
	mv "$queue_file~" "$queue_file"
	atomic
done
