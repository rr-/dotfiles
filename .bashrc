# vim: syntax=sh

#meta information
SOURCE="${BASH_SOURCE[0]}"
while [ -h "$SOURCE" ]; do
    DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"
    SOURCE="$(readlink "$SOURCE")"
    [[ $SOURCE != /* ]] && SOURCE="$DIR/$SOURCE"
done
DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"

if [ -t 0 ]; then
    interactive=1
else
    interactive=0
fi

#the one and only editor
EDITOR=vim
export EDITOR
alias editor="$EDITOR"

#useful PATH
export PATH=${PATH}:"$DIR/bin":"$DIR/bin/ext"

#rvm stuff
export PATH=${PATH}:${HOME}/.rvm/bin
[ -s ~/.rvm/scripts/rvm ] && source ~/.rvm/scripts/rvm

#various shell options
if [ $interactive -eq 1 ]; then
    stty -ixon
    export HISTIGNORE="fg*"
    export HISTCONTROL=ignoredups #ignore duplicate commands in history

    shopt -s histappend #append to the history file, don't overwrite it
    shopt -s globstar #allow ** recursive wildcards
    shopt -s checkwinsize #check the window size after each command and, if necessary, update the values of LINES and COLUMNS.
    shopt -s nocasematch #case insensitive matching
fi

#cool command prompt
PS1='\[\e[1;31m\]'
PS1+='\u@\h'
PS1+='\[\e[0;37m\]'
PS1+=':'
PS1+='\[\e[0;32m\]'
PS1+='\w'
PS1+='\[`if [ $? = 0 ]; then echo -e "\e[0;37m"; else echo -e "\e[1;31m"; fi`\]'
PS1+='\$ '
PS1+='\[\e[0m\]'
#titlebar
PS1+='\[\e]0;\u@\h \w\007\]'


#aliases w/ colors
if [ -x /usr/bin/dircolors ]; then
    test -r ~/.dircolors && eval "$(dircolors -b ~/.dircolors)" || eval "$(dircolors -b)"
    ls='ls --color=auto'
    alias dir='dir --color=auto'
    alias vdir='vdir --color=auto'

    alias grep='grep --color=auto'
    alias fgrep='fgrep --color=auto'
    alias egrep='egrep --color=auto'
else
    ls=ls
fi

#aliases
alias datediff="$DIR/../sh-date-diff/datediff.sh"
alias plen='tl pl en'
alias enpl='tl en pl'
alias rfn='date "+%Y%m%d_%H%M%S"|tr -d "\r\n"'
alias isvim='ps ux|grep vim|grep -v grep'

alias ls="$ls"' -vhF1 --group-directories-first'
alias ll="$ls"' -vhFlX --group-directories-first'
alias la="$ls"' -vhFlXA --group-directories-first'

#legacy aliases
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

alias dark='rm ~/.minttyrc && ln -s "'"$DIR"'/.minttyrc-dark" ~/.minttyrc; echo -e "set background=dark\ncolor sorcerer">~/.vimrc-background'
alias light='rm ~/.minttyrc && ln -s "'"$DIR"'/.minttyrc-light" ~/.minttyrc; echo -e "set background=light\ncolor hemisu">~/.vimrc-background'

if [ -e /dev/clipboard ]; then
    alias clip='cat >/dev/clipboard'
fi

#additional config
hostname=$(hostname)
if [[ hostname -eq luna ]]; then
    #some aliases
    alias subs="$DIR/../sh-napiprojekt/subs.sh"
    alias wallchanger="$DIR/../sh-wall-changer/sh-wall-changer.exe"
    export PATH=${PATH}:':/cygdrive/z/software/utilities/php5.6.2'

    #autocompletion for imgop.sh
    _imgop()
    {
        local cur=${COMP_WORDS[COMP_CWORD]}
        if [[ $COMP_CWORD -eq 1 ]]; then
            COMPREPLY=( $(compgen -W 'degrade downgrade fix-anamorphic fix-png stitch' -- $cur) )
        else
            COMPREPLY=( $(compgen -A file -- $cur) )
        fi
    }
    complete -F _imgop imgop.sh
elif [[ hostname -eq burza ]]; then
    #command prompt in different color
    PS1=$(echo "$PS1"|sed 's/1;31/0;36/')
fi
