#!/bin/sh
find -type f -name '*.png' -print0|while read -d $'\0' p; do
	fmt=$(identify -format "%r" "$p");
	[[ $fmt == 'PseudoClassGrayMatte' ]] && convert "$p" -alpha off "$p" && echo "$p";
done
