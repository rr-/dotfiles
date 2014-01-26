#the one and only editor
EDITOR=vim
export EDITOR
alias editor="$EDITOR"

#get path to self
SOURCE="${BASH_SOURCE[0]}"
while [ -h "$SOURCE" ]; do
	DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"
	SOURCE="$(readlink "$SOURCE")"
	[[ $SOURCE != /* ]] && SOURCE="$DIR/$SOURCE"
done
DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"

#useful PATH
export PATH=${PATH}:"$DIR"

#various shell options
export HISTCONTROL=ignoredups #ignore duplicate commands in history
shopt -s histappend #append to the history file, don't overwrite it
shopt -s globstar #allow ** recursive wildcards
shopt -s checkwinsize #check the window size after each command and, if necessary, update the values of LINES and COLUMNS.
shopt -s nocasematch #case insensitive matching

#cool command prompt
PS1='\[\e[1;31m\]'
PS1+='\u@\h'
PS1+='\[\e[0;37m\]'
PS1+=':'
PS1+='\[\e[0;32m\]'
PS1+='\w'
PS1+='\[\e[1;34m\]'
PS1+='($SHLVL:\#) '
PS1+='\[\e[0m\]'
PS1+='\$ '
PS1+='\[\e]0;\u@\h \w\007\]'


#aliases w/ colors
if [ -x /usr/bin/dircolors ]; then
	test -r ~/.dircolors && eval "$(dircolors -b ~/.dircolors)" || eval "$(dircolors -b)"
	alias ls='ls -vhF1 --color=auto --group-directories-first'
	alias ll='ls -vhFlX --color=auto --group-directories-first'
	alias la='ls -vhFlXA --color=auto --group-directories-first'
	alias dir='dir --color=auto'
	alias vdir='vdir --color=auto'

	alias grep='grep --color=auto'
	alias fgrep='fgrep --color=auto'
	alias egrep='egrep --color=auto'
else
	alias ls='ls -vhF1 --group-directories-first'
	alias ll='ls -vhFlX --group-directories-first'
	alias la='ls -vhFlXA --group-directories-first'
fi


#aliases w/o colors
alias datediff="$DIR/../sh-date-diff/datediff.sh"
alias tl="$DIR/../sh-translator/tl.py"
alias plen='tl pl en'
alias enpl='tl en pl'
alias rfn='date "+%Y%m%d_%H%M%S"|tr -d "\r\n"'
alias isvim='ps ux|grep vim|grep -v grep'


#legacy aliases
command -v hd >/dev/null 2>&1 || alias hd='od -Ax -t x1'
command -v poweroff >/dev/null 2>&1 && [[ ! $(uname) =~ cygwin ]] || alias poweroff='shutdown -s now'
command -v reboot >/dev/null 2>&1 && [[ ! $(uname) =~ cygwin ]] || alias reboot='shutdown -r now'


#host-specific config
hostname=$(hostname)
if [ -f "$DIR/bashcfg-$hostname.sh" ]; then
	. "$DIR/bashcfg-$hostname.sh"
fi
