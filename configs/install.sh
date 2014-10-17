#!/bin/bash
for x in .bashrc .vimrc .vim .inputrc .minttyrc .bash_profile .gitconfig; do
	source=$HOME/$x
	target=$source~
	rm -rf "$target"
	if [ -e "$source" ] || [ -L "$source" ]; then
		mv "$source" "$target"
	fi
done

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
mkdir "$HOME/.vim"
ln -s "$DIR/vim-plugins" "$HOME/.vim/bundle"
ln -s "$DIR/vimrc" "$HOME/.vimrc"
ln -s "$DIR/bash_config" "$HOME/.bashrc"
ln -s "$DIR/bash_config" "$HOME/.bash_profile"
ln -s "$DIR/inputrc" "$HOME/.inputrc"
ln -s "$DIR/minttyrc" "$HOME/.minttyrc"
ln -s "$DIR/gitconfig" "$HOME/.gitconfig"

shopt -s nocasematch
if [[ "$(uname)" =~ cygwin ]]; then
	for x in .bashrc .vimrc .vim .inputrc .minttyrc; do
		winpath=$(cygpath -w "$HOME")\\$x
		attrib +h +s "$winpath"
	done
fi
