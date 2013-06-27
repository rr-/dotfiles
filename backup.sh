#!/bin/bash
. config.ini
[ "$(hostname)" != "$desktop" ] && echo "Must be run on $desktop" 1>&2 && exit 1

cmd='rsync -azK --delete-after -e ssh'
$cmd "$user@$server:/etc/" "/cygdrive/z/clutter/backup-$server/etc"
$cmd "$user@$server:/home/$user/" "/cygdrive/z/clutter/backup-$server/home/$user/" --exclude "img/" --exclude "backup-$desktop/"
$cmd "$user@$server:/home/srv/" "/cygdrive/z/clutter/backup-$server/home/srv/" --exclude "www/mal-dev/"
$cmd "/cygdrive/z/clutter/" "$user@$server:/home/$user/backup-$desktop/clutter/" --exclude "backup-$server/"
$cmd "/cygdrive/z/img/" "$user@$server:/home/$user/backup-$desktop/img/" --exclude "net/"
$cmd "/cygdrive/z/mgr/" "$user@$server:/home/$user/backup-$desktop/mgr/"
$cmd "/cygdrive/z/text/" "$user@$server:/home/$user/backup-$desktop/text/"
$cmd "/cygdrive/z/src/" "$user@$server:/home/$user/backup-$desktop/src/"
