#!/bin/sh

if [ -d /etc/X11/xinit/xinitrc.d ]; then
    for f in /etc/X11/xinit/xinitrc.d/*; do
        [ -x "$f" ] && . "$f"
    done
    unset f
fi

xrandr --output DVI-I-1 --auto --output HDMI-0 --auto --left-of DVI-I-1
xrdb ~/.config/Xresources

#set Polish keyboard
setxkbmap pl
#set app menu as mod3
xmodmap -e 'remove Mod4 = Hyper_L'
xmodmap -e 'add Mod3 = Hyper_L'
xmodmap -e 'keycode 135 = Menu'
xmodmap -e 'keysym Menu = Hyper_L'

#enable transparency manager
#this is also supposed to eliminate problems with tearing.
/usr/bin/compton -b --backend glx --paint-on-overlay --vsync opengl-swc

exec i3
