#!/bin/bash

shopt -s nocasematch
remote_root_dir="/home/rr-/img/"
dst_root_dir="/cygdrive/z/img/net/"
remote_user=rr-
remote_addr=burza
local_addr=luna
min_width=500
min_height=500
min_size=$[$min_width*$min_height]

[ "$(hostname)" != "$local_addr" ] && echo "Must be run on $local_addr" 1>&2 && exit 1

#prepare transit dir
transit_root_dir=/cygdrive/z/hub/img-tmp

#download the images
rsync --info=progress2 -a --remove-source-files "$remote_user@$remote_addr:$remote_root_dir" "$transit_root_dir"

#distribute the images
find "$transit_root_dir" -type f -print0|while read -d '' -r src_file; do
	echo -n "$src_file "

	#preprocess image
	if [[ "$src_file" =~ .*\.(jpg|png) ]]; then
		read format dimensions < <(identify -format '%r %w*%h' "$src_file" 2>/dev/null)
		if [ $? -eq 0 ]; then
			size=$(echo "$dimensions"|bc)
			#check if too small
			if [[ "$size" -lt "$min_size" ]]; then
				echo "$dimensions < $min_width*$min_height"
				rm "$src_file"
				continue
			fi
			#convert certain pngs for ancient versions of acdsee
			if [[ "$format" == "DirectClassGrayMatte" ]]; then
				convert "$src_file" -type TrueColorMatte png32:"$src_file"
				echo -n "converted; ";
			fi
		fi
	fi

	dst_file="$dst_root_dir${src_file##$transit_root_dir}"
	dst_file="$(echo $dst_file|sed -e 's/[^/]*\.2chan\.net/2chan/;s/\w\+\.\(4chan\|4cdn\)\.org/4chan/;s/\/src//')"
	dst_dir="$(dirname "$dst_file")"
	mkdir -p "$dst_dir"
	mv "$src_file" "$dst_file" && echo 'ok'
done

#remove empty directores
find "$transit_root_dir" -depth -type d -exec rmdir --ignore-fail-on-non-empty "{}" \;
ssh "$remote_user@$remote_addr" "bash -c 'find \"$remote_root_dir\" -depth -mindepth 1 -type d -exec rmdir --ignore-fail-on-non-empty \"{}\" \;'"
