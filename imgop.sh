#!/bin/bash

op="$1"
shift 1
case "$op" in
	degrade|downgrade)
		for file; do
			[ -f "$file" ] || continue
			echo $file
			mv "$file" "$file~"
			new=${file%.*}.jpg
			convert "$file~[0]" -quality 80 "jpg:$new"
		done
		;;
	fix-anamorphic)
		for file; do
			[ -f "$file" ] || continue
			w=$(identify -format "%w" "$file")
			h=$(identify -format "%h" "$file")
			nw=$(( $h * 16 / 9 ))
			nh=$h
			echo "$file: ${w}x${h} -> ${nw}x${nh}"
			mv "$file" "$file~"
			convert "$file~" -resize "${nw}x${nh}!" "$file"
		done
		;;
	fix-png)
		for file; do
			[ -f "$file" ] || continue
			if [[ "$file" = *.png ]]; then
				fmt=$(identify -format "%r" "$file");
				if [[ "$fmt" == "PseudoClassGrayMatte" ]]; then
					echo "$file"
					convert "$file" -alpha off "$file"
				fi
			fi
		done
		;;
	base64)
		for file; do
			[ -f "$file" ] ||continue
			if [[ "$file" = *.png ]]; then
				echo -n data:image/png\;base64,
			elif [[ "$file" = *.gif ]]; then
				echo -n data:image/png\;base64,
			fi
			base64 -w0 <"$file"
			echo
		done
		;;
	stitch)
		convert -border 0x1 -bordercolor black "$@" -append -trim "stitched.jpg"
		;;
	*)
		echo "Unknown operation: $op" 1>&2
		exit 1
		;;
esac
