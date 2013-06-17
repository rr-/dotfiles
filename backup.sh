#!/bin/sh
desktop=luna
server=burza
user=rr-
[ `hostname` != $desktop ] && echo "Must be run on $desktop" 1>&2 && exit 1

cmd='rsync -azK --delete-after -e ssh'
$cmd $user@$server:/etc/ ~/clutter/backup-$server/etc
$cmd $user@$server:/home/rr-/ ~/clutter/backup-$server/home/rr-/ --exclude img/ --exclude backup-$desktop/
$cmd $user@$server:/home/srv/ ~/clutter/backup-$server/home/srv/ --exclude www/mal-dev/
$cmd ~/clutter/ $user@$server:~/backup-luna/clutter/ --exclude backup-$server/
$cmd ~/img/ $user@$server:~/backup-luna/img/ --exclude net/
$cmd ~/mgr/ $user@$server:~/backup-luna/mgr/
$cmd ~/text/ $user@$server:~/backup-luna/text/
$cmd ~/src/ $user@$server:~/backup-luna/src/
