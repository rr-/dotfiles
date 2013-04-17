#!/bin/bash
[[ -z "$@" ]] && ( echo "No files selected" && exit 1 )

for file in "$@"; do
	echo "Processing $file..."

	md5=`head "$file" -c 10485760|md5sum -b -|cut -f 1 -d ' '`
	add=(0 13 16 11 5)
	mul=(2 2 5 4 3)
	idx=(14 3 6 8 2)
	checksum=''
	for i in {0..4}; do
		a=${add[@]:$i:1}
		m=${mul[@]:$i:1}
		x=${idx[@]:$i:1}
		t=$(( $a + $((0x${md5:$x:1})) ))
		v=$((0x${md5:$t:2}))
		checksum+=$(printf '%x' $(( $v * $m )) | tail -c 1 )
	done

	url="http://napiprojekt.pl/unit_napisy/dl.php?l=PL&f=$md5&t=$checksum&v=other&kolejka=false&nick=&pass=&napios=posix"
	tmpfile="$(mktemp)"
	wget "$url" -qO "$tmpfile"

	if [[ "$(head "$tmpfile" -c 3)" == "NPc" ]]; then
		echo "Subtitles not found."
	else
		outfile="${file%.*}.sub"
		napipass="iBlm8NTigvru0Jr0"
		/usr/bin/7z x -q -y -so -p"$napipass" "$tmpfile" > "$outfile"
		[[ $? -eq 0 ]] && echo "Subtitles stored OK." || echo "Error extracting."
	fi

	rm "$tmpfile"
done
