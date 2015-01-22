#!/bin/sh
if [ "$(id -u)" != '0' ]; then
	echo 'This script must be run as root' 1>&2
	exit 1
fi

tar cvpzf /backup.tgz \
	--exclude=/proc \
	--exclude=/lost+found \
	--exclude=/backup.tgz \
	--exclude=/mnt \
	--exclude=/sys \
	--exclude=/dev \
	/
