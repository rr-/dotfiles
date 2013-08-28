#!/bin/bash
. config.ini
[ "$(hostname)" != "$desktop" ] && echo "Must be run on $desktop" 1>&2 && exit 1

backup_user=backup
server_backup=( /etc "/home/$user" /home/srv )
desktop_backup=( clutter img text src )

for x in ${server_backup[@]}; do
	echo "$server --> $desktop: $x"
	rsync --chmod=D=rwrxrxrx,F=rwrr -avzKR --delete-during -e "ssh -i /home/rr-/.ssh/id_rsa" "$user@$server:$x/" "/cygdrive/z/backup-$server/" --exclude "/home/$user/img/" --exclude "/home/srv/www/mal-dev/data/"
	echo
done

for x in ${desktop_backup[@]}; do
	echo "$desktop --> $server: $x"
	rsync --chmod=D=rwxrxrx,F=rwrr -avzKR --delete-during -e "ssh -i /home/rr-/.ssh/id_rsa" "/cygdrive/z/$x/" "$backup_user@$server:/home/backup/backup-$desktop/" --exclude "/cygdrive/z/img/net/"
	echo
done
