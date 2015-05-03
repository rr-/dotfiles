SOURCE=$(readlink ${ZDOTDIR-~}/.zshrc)
DIR=${SOURCE:h}
HOST=$(hostname)

# environment variables
export EDITOR=vim                       # for stuff that need interactive editor
export PATH=$DIR/bin:$DIR/bin/ext:$PATH # PATH for all the goodies in this repo
export PATH=$PATH:$HOME/.rvm/bin        # PATH to rvm
    [ -s ~/.rvm/scripts/rvm ] &&        # Check if rvm exists
        source ~/.rvm/scripts/rvm       # And run its init script

# autocomplete
autoload -Uz compinit                   # initialize autocompletion engine
compinit                                # initialize autocompletion engine (2)
zstyle ':completion:*' matcher-list 'm:{a-zA-Z}={A-Za-z}' # case insensitive
setopt NO_NOMATCH                       # if extended glob fails, run cmd as-is

# miscellaneous
unsetopt beep                           # disable beep on errors
setopt correct                          # enable [nyae] correction
setopt auto_cd                          # "cd /usr/" becomes "/usr/"
setopt nocasematch                      # regex should work case-insensitive
WORDCHARS='*?_-.[]~=&;!#$%^(){}<>'      # what kill-word should delete

# history
HISTFILE=~/.histfile                    # set path to history file
HISTSIZE=1000                           # how many entries in history
SAVEHIST=1000                           # how many entries in history (2)
setopt appendhistory                    # append lines (for concurrent sessions)
setopt histignoredups                   # don't put duplicates in history

# basic key bindings
bindkey -e                              # use Emacs keybindings
stty -ixon                              # reclaim ctrl+q for Vim
stty stop undef                         # reclaim ctrl+s for Vim

# key bindings for terminal emulator
if [ "$TERM" =~ rxvt ]; then
    bindkey "\e[3~"   delete-char           # delete
    bindkey '\e[1~'   beginning-of-line     # home and ctrl+home
    bindkey '\e[4~'   end-of-line           # end adn ctrl+end
    bindkey '^H'      backward-kill-word    # ctrl+backspace
    bindkey "^[3^"    kill-word             # ctrl+delete
    bindkey '\eOd'    backward-word         # ctrl+left
    bindkey '\eOc'    forward-word          # ctrl+right
else
    bindkey "\e[3~"   delete-char           # delete
    bindkey '\eOH'    beginning-of-line     # home
    bindkey '\eOF'    end-of-line           # end
    bindkey ';5H'     beginning-of-line     # ctrl+home
    bindkey ';5F'     end-of-line           # ctrl+end
    bindkey '^_'      backward-kill-word    # ctrl+backspace
    bindkey "\e[3;5~" kill-word             # ctrl+delete
    bindkey ';5D'     backward-word         # ctrl+left
    bindkey ';5C'     forward-word          # ctrl+right
fi

    # necessary for the above to work
    if [[ -n ${terminfo[smkx]} ]] && [[ -n ${terminfo[rmkx]} ]]; then
        function zle-line-init () {
            echoti smkx
        }
        function zle-line-finish () {
            echoti rmkx
        }
        zle -N zle-line-init
        zle -N zle-line-finish
    fi

# cool command prompt
PS1=$'%{\e[1;31m%}%n@%M'               # user@host
PS1+=$'%{\e[0;37m%}:'                  # :
PS1+=$'%{\e[0;32m%}%~'                 # path relative to $HOME
PS1+=$'%(?.%{\e[0;37m%}.%{\e[1;31m%})$ ' # colored $ depending on last exit code
PS1+=$'%{\e[0m%}'                      # reset colors
PS1+=$'%{\e]0;%n@%M:%~\007%}'          # add titlebar user@host:~/

# command prompt in different color for SSH sessions
if [ -n "$SSH_CLIENT" ] || [ -n "$SSH_TTY" ]; then
    PS1=$(echo "$PS1"|sed 's/1;31/0;36/')
fi

# aliases related to colors
if [[ -x "`whence -p dircolors`" ]]; then
    eval `dircolors`
    alias ls='ls --color=auto'
    alias grep='grep --color=auto'
    alias fgrep='fgrep --color=auto'
    alias egrep='egrep --color=auto'
fi

# aliases
alias ls="`whence ls`"' -vhF1 --group-directories-first'
alias ll="`whence ls`"' -lX --group-directories-first'
alias la="`whence ls`"' -lXA --group-directories-first'

alias plen='tl pl en'
alias enpl='tl en pl'
alias rfn='date "+%Y%m%d_%H%M%S"'
alias isvim='ps ux|grep vim|grep -v grep'

alias dark='term-lightness 0'
alias light='term-lightness 1'

# legacy aliases
command -v hd >/dev/null 2>&1 || alias hd='od -Ax -t x1'
if ! command -v poweroff >/dev/null 2>&1; then
    [[ $(uname) =~ cygwin ]] && alias poweroff='shutdown /p /f' || alias poweroff='shutdown -s now'
fi
if ! command -v reboot >/dev/null 2>&1; then
    [[ $(uname) =~ cygwin ]] && alias reboot='shutdown /r /t 0 /f' || alias reboot='shutdown -r now'
fi
command -v phpunit >/dev/null 2>&1 || alias phpunit='php vendor/phpunit/phpunit/phpunit'
command -v composer >/dev/null 2>&1 || alias composer='php composer'
command -v rubocop >/dev/null 2>&1 || alias rubocop='~/.gem/**/gems/rubocop*/bin/rubocop'
command -v bundle >/dev/null 2>&1 || alias bundle='~/.gem/**/gems/bundle*/bin/bundle'
[ -e /dev/clipboard ] && alias clip='cat >/dev/clipboard'
