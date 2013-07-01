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
. config.ini


#various shell options
export HISTCONTROL=ignoredups #ignore duplicate commands in history
shopt -s histappend #append to the history file, don't overwrite it
shopt -s globstar #allow ** recursive wildcards
shopt -s checkwinsize #check the window size after each command and, if necessary, update the values of LINES and COLUMNS.
shopt -s nocasematch #case insensitive matching

#cool command prompt
case "$TERM" in
xterm*|rxvt|linux|screen*)
	if [ "$(hostname)" = "$server" ]; then
		COL='\[\e[0;36m\]'
	else
		COL='\[\e[1;31m\]'
	fi
	PS1=$COL'\u@\h\[\e[0;37m\]:\[\e[0;32m\]\w\[\e[1;34m\]($SHLVL:\#) \[\e[0m\]\$ '
	unset COL
	;;
*)
	PS1="\[\e]0;\u@\h: \w\a\]$PS1"
	;;
esac


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
alias tl="$DIR/../sh-translator/tl.py"
alias plen='tl pl en'
alias enpl='tl en pl'
alias rfn='date "+%Y%m%d_%H%M%S"'
alias isvim='ps ux|grep vim|grep -v grep'

#legacy aliases
command -v hd >/dev/null 2>&1 || alias hd='od -Ax -t x1'
command -v poweroff >/dev/null 2>&1 && [[ ! $(uname) =~ cygwin ]] || alias poweroff='shutdown -s now'
command -v reboot >/dev/null 2>&1 && [[ ! $(uname) =~ cygwin ]] || alias reboot='shutdown -r now'

#autocompletion for imgop.py
_imgop()
{
	local cur=${COMP_WORDS[COMP_CWORD]}
	if [[ $COMP_CWORD -eq 1 ]]; then
		COMPREPLY=( $(compgen -W "degrade downgrade fix-anamorphic fix-png stitch" -- $cur) )
	else
		COMPREPLY=( $(compgen -A file -- $cur) )
	fi
}
complete -F _imgop imgop.py
