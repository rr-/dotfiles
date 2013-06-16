#!/usr/bin/bash
if [ -e /cygdrive/z/stitched.jpg ]; then
	unlink /cygdrive/z/stitched.jpg
fi
if [ -e /cygdrive/z/stitched.png ]; then
	unlink /cygdrive/z/stitched.png
fi

montage "$@" -tile 1x -geometry +0+0,5% -background black /cygdrive/z/stitched.png
convert /cygdrive/z/stitched.png -trim /cygdrive/z/stitched.jpg

unlink /cygdrive/z/stitched.png