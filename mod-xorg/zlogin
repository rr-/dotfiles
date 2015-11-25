if [ -z "$SSH_CLIENT" ] && [ -z "$SSH_TTY" ]; then
    if command -v startx &>/dev/null; then
        [[ -z $DISPLAY && $XDG_VTNR -eq 1 ]] && exec startx -bs -store
    else
        echo 'startx not found'
    fi
fi
