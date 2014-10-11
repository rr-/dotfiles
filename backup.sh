#!/bin/bash
desktop=luna
server=burza
server_addr=sakuya.pl
user=rr-
[ "$(hostname)" != "$desktop" ] && echo "Must be run on $desktop" 1>&2 && exit 1

backup_user=backup
server_backup=( /etc "/home/$user" /home/srv )
desktop_backup=( software/utilities clutter img text src )
transit_dir=/cygdrive/z/hub/backup-tmp

for x in ${server_backup[@]}; do
	echo "$server --> $desktop: $x"
	rsync -T "$transit_dir" \
		--chmod=D=rwrxrxrx,F=rwrr \
		--info=progress2 \
		-aKR \
		--delete-during \
		"$user@$server_addr:$x/" \
		"/cygdrive/z/backup-$server/" \
		--exclude "/home/$user/img/" \
		--exclude "/home/srv/www/mal-dev/data/" \
		--exclude "/home/srv/www/booru-dev/public_html/data/"
	echo
done

for x in ${desktop_backup[@]}; do
	echo "$desktop --> $server: $x"
	rsync -T "$transit_dir" \
		--chmod=D=rwxrxrx,F=rwrr \
		--info=progress2 \
		-aKR \
		--delete-during \
		"/cygdrive/z/$x/" \
		"$backup_user@$server_addr:/home/backup/backup-$desktop/" \
		--exclude "/cygdrive/z/img/net/" \
		--exclude "/cygdrive/z/software/utilities/cygwin"
	echo
done
