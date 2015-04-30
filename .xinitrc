#!/bin/sh

if [ -d /etc/X11/xinit/xinitrc.d ]; then
    for f in /etc/X11/xinit/xinitrc.d/*; do
        [ -x "$f" ] && . "$f"
    done
    unset f
fi

xrandr --output DVI-0 --auto --output HDMI-0 --auto --left-of DVI-0
xrdb ~/.Xresources

exec i3
