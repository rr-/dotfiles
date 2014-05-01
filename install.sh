#!/bin/bash
for x in .bashrc .vimrc .vim .inputrc; do
	mv "$HOME/$x" "$HOME/$x~"
done

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
ln -s "$DIR/bashcfg.sh" "$HOME/.bashrc"
ln -s "$DIR/vimcfg.vim" "$HOME/.vimrc"
ln -s "$DIR/vim" "$HOME/.vim"
ln -s "$DIR/inputrc" "$HOME/.inputrc"
ln -s "$DIR/minttyrc" "$HOME/minttyrc"

shopt -s nocasematch
if [[ "$(uname)" =~ cygwin ]]; then
	for x in .bashrc .vimrc .vim .inputrc .minttyrc; do
		winpath=$(cygpath -w "$HOME")\\$x
		attrib +h +s "$winpath"
	done
fi
