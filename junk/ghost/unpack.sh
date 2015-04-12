#!/bin/sh
if [ "$(id -u)" != '0' ]; then
	echo 'This script must be run as root' 1>&2
	exit 1
fi

if [ ! -f /backup.tgz ]; then
	echo 'Backup not found.' 1>&2
	return 1
fi

tar xvpzf /backup.tgz -C /
