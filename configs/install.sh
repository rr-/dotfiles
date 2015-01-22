#!/bin/bash
for x in .bashrc .vimrc .vim/vundle .inputrc .minttyrc .bash_profile .gitconfig .mplayer; do
	source=$HOME/$x
	target=$source~

	if [ -e "$target" ]; then
		echo Removing old backup "$target"
		rm -rf "$target"
	fi

	if [ -e "$source" ]; then
		if [ -L "$source" ]; then
			echo Removing symlink "$source"
			rm "$source"
		else
			echo Not a symlink: "$source". Aborting.
			exit 1
		fi
	fi
done

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
[ ! -d "$HOME/.vim" ] && mkdir "$HOME/.vim"
[ ! -d "$HOME/.vim/undo" ] && mkdir "$HOME/.vim/undo"
[ ! -d "$HOME/.vim/backup" ] && mkdir "$HOME/.vim/backup"
[ ! -d "$HOME/.vim/swap" ] && mkdir "$HOME/.vim/swap"

echo "Installing vim configuration manager"
ln -s "$DIR/vundle" "$HOME/.vim/vundle"

echo "Installing vimrc"
ln -s "$DIR/vimrc" "$HOME/.vimrc"

echo "Installing bashrc"
ln -s "$DIR/bash_config" "$HOME/.bashrc"

echo "Installing bashprofile"
ln -s "$DIR/bash_config" "$HOME/.bash_profile"

echo "Installing inputrc"
ln -s "$DIR/inputrc" "$HOME/.inputrc"

echo "Installing minttyrc"
ln -s "$DIR/minttyrc" "$HOME/.minttyrc"

echo "Installing gitconfig"
ln -s "$DIR/gitconfig" "$HOME/.gitconfig"

echo "Installing mplayer"
ln -s "$DIR/mplayer" "$HOME/.mplayer"

shopt -s nocasematch
if [[ "$(uname)" =~ cygwin ]]; then
	for x in .bashrc .vimrc .vim .inputrc .minttyrc .bash_profile .gitconfig .mplayer; do
		winpath=$(cygpath -w "$HOME")\\$x
		attrib +h +s "$winpath"
		echo "Hiding $winpath"
	done
fi
