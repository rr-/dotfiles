#!/bin/bash

function install_link {
	source=$1
	target=$HOME/$2

	echo "Installing $source to $target"

	if [ -h "$target" ]; then
		echo Removing old symlink "$target"
		rm "$target"
	else
		if [ -e "$target" ]; then
			echo Not a symlink: "$target". Aborting.
			exit 1
		fi
	fi

	ln -s "$source" "$target"
}

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
[ ! -d "$HOME/.vim" ] && mkdir "$HOME/.vim"
[ ! -d "$HOME/.vim/undo" ] && mkdir "$HOME/.vim/undo"
[ ! -d "$HOME/.vim/backup" ] && mkdir "$HOME/.vim/backup"
[ ! -d "$HOME/.vim/swap" ] && mkdir "$HOME/.vim/swap"
[ ! -d "$HOME/.vim/spell" ] && mkdir "$HOME/.vim/spell"

install_link "$DIR/vim-spellcheck/pl.utf-8.add" ".vim/spell/pl.utf-8.add"
install_link "$DIR/vim-spellcheck/en.utf-8.add" ".vim/spell/en.utf-8.add"
install_link "$DIR/vundle" ".vim/vundle"
install_link "$DIR/vimrc" ".vimrc"
install_link "$DIR/zshrc" ".zshrc"
install_link "$DIR/bash_config" ".bashrc"
install_link "$DIR/bash_config" ".bash_profile"
install_link "$DIR/inputrc" ".inputrc"
install_link "$DIR/minttyrc-light" ".minttyrc"
install_link "$DIR/gitconfig" ".gitconfig"
install_link "$DIR/mplayer" ".mplayer"
install_link "$DIR/mpv" ".mpv"

shopt -s nocasematch
if [[ "$(uname)" =~ cygwin ]]; then
	cd "$HOME"
	echo "Hiding dotfiles in $HOME"
	attrib +h +s .\*
fi
