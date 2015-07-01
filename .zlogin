if command -v startx &>/dev/null; then
    if [[ `hostname` == "bus" ]]; then
        fbterm
    else
        [[ -z $DISPLAY && $XDG_VTNR -eq 1 ]] && exec startx -bs -store
    fi
fi
