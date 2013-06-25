#!/bin/bash
desktop=luna
server=burza
user=rr-
[ `hostname` != $desktop ] && echo "Must be run on $desktop" 1>&2 && exit 1

shopt -s nocasematch
remote_root_dir='/home/rr-/img/dead/'
transit_root_dir='/cygdrive/z/hub/img/'
dst_root_dir='/cygdrive/z/img/net/'
min_width=500
min_height=500
min_size=$[$min_width*$min_height]

#download the images
rsync -avz --remove-source-files "$server:$remote_root_dir" "$transit_root_dir"

#distribute the images
find "$transit_root_dir" -type f -print0|while read -d '' -r src_file
do
	echo -n "$src_file "

	#check image size
	if [[ "$src_file" =~ .*\.(jpg|png) ]]
	then
		dimensions=$(identify -format '%w*%h' "$src_file" 2>/dev/nll)
		if [ $? -eq "0" ]
		then
			size=$(echo $dimensions|bc)
			if [ "$size" -lt "$min_size" ]; then
				echo "$dimensions < $min_width*$min_height"
				rm "$src_file"
				continue
			fi
		fi
	fi

	dst_file=$dst_root_dir${src_file##$transit_root_dir}
	dst_file=$(echo "$dst_file"|sed -e 's/[^/]*\.2chan\.net/2chan/;s/images\.4chan\.org/4chan/;s/\/src//')
	dst_dir=$(dirname "$dst_file")
	mkdir -p "$dst_dir"
	mv "$src_file" "$dst_file" && echo 'ok'
done

#remove empty directores
find "$transit_root_dir" -depth -type d -exec rmdir --ignore-fail-on-non-empty "{}" \;
ssh $server "bash -c 'find \"$remote_root_dir\" -depth -type d -exec rmdir --ignore-fail-on-non-empty \"{}\" \;'"
