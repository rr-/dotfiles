#!/bin/bash
. config.ini
[ "$(hostname)" != "$desktop" ] && echo "Must be run on $desktop" 1>&2 && exit 1

cmd='rsync -azK --delete-after -e ssh'
$cmd "$user@$server:/etc/" "~/clutter/backup-$server/etc"
$cmd "$user@$server:/home/$user/ ~/clutter/backup-$server/home/$user/" --exclude "img/" --exclude "backup-$desktop/"
$cmd "$user@$server:/home/srv/ ~/clutter/backup-$server/home/srv/" --exclude "www/mal-dev/"
$cmd "~/clutter/" "$user@$server:~/backup-$desktop/clutter/" --exclude "backup-$server/"
$cmd "~/img/" "$user@$server:~/backup-$desktop/img/" --exclude "net/"
$cmd "~/mgr/" "$user@$server:~/backup-$desktop/mgr/"
$cmd "~/text/" "$user@$server:~/backup-$desktop/text/"
$cmd "~/src/" "$user@$server:~/backup-$desktop/src/"
