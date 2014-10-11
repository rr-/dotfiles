#!/bin/bash
remote_root_dir="/home/rr-/img/"
dst_root_dir="/cygdrive/z/img/net/"
remote_user=rr-
remote_addr=burza
local_addr=luna
min_width=500
min_height=500
min_size=$[$min_width*$min_height]

[ "$(hostname)" != "$local_addr" ] && echo "Must be run on $local_addr" 1>&2 && exit 1

shopt -s extglob
shopt -s nocasematch
trap "exit" INT

#prepare transit dir
transit_root_dir=/cygdrive/z/hub/img-tmp

#download the images
rsync --info=progress2 -a --remove-source-files "$remote_user@$remote_addr:$remote_root_dir" "$transit_root_dir"

#distribute the images
find "$transit_root_dir" -depth -type d -print0|while read -d '' -r src_folder; do
	dst_folder="$dst_root_dir${src_folder##$transit_root_dir}"
	dst_folder="${dst_folder/*([^\/]).2chan.net/2chan}"
	dst_folder="${dst_folder/*([^\/]).@(4chan|4cdn).org/4chan}"
	dst_folder="${dst_folder/\/src/}"

	echo $src_folder $dst_folder
	mkdir -p "$dst_folder"

	find "$src_folder" -type f -maxdepth 1 -print0|while read -d '' -r src_file; do
		dst_file="$dst_folder/$(basename "$src_file")"

		echo -n "$src_file "

		#preprocess image
		if [[ "$src_file" =~ .*\.(jpg|png) ]]; then
			read format dimensions < <(identify -format '%r %w*%h' "$src_file" 2>/dev/null)
			if [ $? -eq 0 ]; then
				size=$(($dimensions))

				#check if too small
				if [[ "$size" -lt "$min_size" ]]; then
					echo "$dimensions < $min_width*$min_height"
					rm "$src_file"
					continue
				fi

				#convert certain pngs for ancient versions of acdsee
				if [[ "$format" == "DirectClassGrayMatte" ]]; then
					convert "$src_file" -type TrueColorMatte png32:"$src_file"
					echo -n "converted; "
				fi
			fi
		fi

		mv "$src_file" "$dst_file" && echo 'ok'
	done
done

#remove empty directores
find "$transit_root_dir" -depth -type d -exec rmdir --ignore-fail-on-non-empty "{}" \;
ssh "$remote_user@$remote_addr" "bash -c 'find \"$remote_root_dir\" -depth -mindepth 1 -type d -exec rmdir --ignore-fail-on-non-empty \"{}\" \;'"
