call plug#begin()
Plug 'junegunn/fzf', { 'dir': '~/.fzf', 'do': './install --all' }
Plug 'junegunn/fzf.vim'                 "open files using fuzzy matching
Plug 'scrooloose/nerdtree'              "file explorer sidebar
Plug 'Lokaltog/vim-easymotion'          "move to any character!
Plug 'vim-airline/vim-airline'          "riced status bar
Plug 'vim-airline/vim-airline-themes'   "riced status bar - themes
Plug 'Yggdroot/indentLine'              "vertical bars showing indent level
Plug 'flazz/vim-colorschemes'           "color schemes!
Plug 'octol/vim-cpp-enhanced-highlight' "improved C++11 highlighting
Plug 'embear/vim-localvimrc'            "local vimrc
Plug 'ntpeters/vim-better-whitespace'   "hilight and strip trailing whitespace
Plug 'tpope/vim-rsi'                    "readline shortcuts in command mode
Plug 'airblade/vim-gitgutter'           "show changed lines in git on margin
Plug 'matze/vim-move'                   "move lines up/down with c-k/c-j
Plug 'rr-/vim-hexdec'                   "convert hex to dec and vice versa
Plug 'junegunn/vim-easy-align'          "replace :column ...
call plug#end()

runtime editor.vim
runtime indent.vim
runtime plugins.vim
runtime keyboard.vim
runtime filetypes.vim
runtime theme.vim
