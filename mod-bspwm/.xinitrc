#!/bin/sh

if [ -d /etc/X11/xinit/xinitrc.d ]; then
    for f in /etc/X11/xinit/xinitrc.d/*; do
        [ -x "$f" ] && . "$f"
    done
    unset f
fi

xrandr --output DVI-I-1 --auto --output HDMI-0 --auto --left-of DVI-I-1
xrdb ~/.config/Xresources
xrdb -override ~/.config/Xresources-theme

#left pointing cursor
xsetroot -cursor_name left_ptr

#set Polish keyboard
setxkbmap pl

#enable transparency manager
#this is also supposed to eliminate problems with tearing.
comptonflags=( -b )
if [[ `hostname` == tornado ]]; then
    # nvidia
    comptonflags+=( --backend glx --vsync opengl-swc --paint-on-overlay )
elif [[ `hostname` == chibi || `hostname` == bus ]]; then
    # amd
    comptonflags+=( --backend xrender --paint-on-overlay --unredir-if-possible )
fi
compton "${comptonflags[@]}"

clipit -d &
autocutsel -fork &
autocutsel -selection PRIMARY -fork &

mpd ~/.config/mpd/mpd.conf &
feh --bg-fill "$HOME/.wallpaper1" "$HOME/.wallpaper2" &
sxhkd &
exec bspwm
