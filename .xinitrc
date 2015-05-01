#!/bin/sh

if [ -d /etc/X11/xinit/xinitrc.d ]; then
    for f in /etc/X11/xinit/xinitrc.d/*; do
        [ -x "$f" ] && . "$f"
    done
    unset f
fi

xrandr --output DVI-I-1 --auto --output HDMI-0 --auto --left-of DVI-I-1
xrdb ~/.config/Xresources

exec i3
