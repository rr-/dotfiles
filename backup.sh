#!/bin/sh
cmd='rsync -azvK --delete-after -e ssh'
$cmd rr-@burza:/etc/ ~/clutter/backup-burza/etc
$cmd rr-@burza:/home/rr-/ ~/clutter/backup-burza/home/rr-/ --exclude 'img/' --exclude 'backup-luna/'
$cmd rr-@burza:/home/srv/ ~/clutter/backup-burza/home/srv/ --exclude 'www/mal-dev/'
$cmd ~/clutter/ rr-@burza:~/backup-luna/clutter/ --exclude 'backup-burza/'
$cmd ~/img/ rr-@burza:~/backup-luna/img/ --exclude 'net/'
$cmd ~/mgr/ rr-@burza:~/backup-luna/mgr/
$cmd ~/text/ rr-@burza:~/backup-luna/text/
$cmd ~/src/ rr-@burza:~/backup-luna/src/
