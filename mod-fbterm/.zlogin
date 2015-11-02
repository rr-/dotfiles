if [ -z "$SSH_CLIENT" ] && [ -z "$SSH_TTY" ]; then
    if command -v fbterm &>/dev/null; then
        fbterm
    else
        echo 'fbterm not found'
    fi
fi
