#the one and only editor
EDITOR=vim
export EDITOR
alias editor=$EDITOR

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
alias plen='~/src/tl.py pl en'
alias enpl='~/src/tl.py en pl'
alias rfn='date "+%Y%m%d_%H%M%S"'
alias isvim='ps ux|grep vim|grep -v grep'
command -v hd >/dev/null 2>&1 || alias hd='od -Ax -t x1'

#ignore duplicate commands in history
export HISTCONTROL=ignoredups

#append to the history file, don't overwrite it
shopt -s histappend

#allow ** recursive wildcards
shopt -s globstar

#check the window size after each command and, if necessary,
#update the values of LINES and COLUMNS.
shopt -s checkwinsize

#set command prompt
case "$TERM" in
xterm*|rxvt|linux|screen*)
	if [ $(hostname) = "burza" ]; then
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

#autocompletion for imgop.py
_imgop()
{
	local cur=${COMP_WORDS[COMP_CWORD]}
	COMPREPLY=( $(compgen -W "degrade downgrade" -- $cur) )
}
complete -F _imgop imgop.py
