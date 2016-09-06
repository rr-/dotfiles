call plug#begin()
Plug 'junegunn/fzf', { 'dir': '~/.fzf', 'do': './install --all' }
Plug 'junegunn/fzf.vim'                 "open files using fuzzy matching
Plug 'Lokaltog/vim-easymotion'          "move to any character!
Plug 'vim-airline/vim-airline'          "riced status bar
Plug 'vim-airline/vim-airline-themes'   "riced status bar - themes
Plug 'Yggdroot/indentLine'              "vertical bars showing indent level
Plug 'flazz/vim-colorschemes'           "color schemes!
Plug 'octol/vim-cpp-enhanced-highlight' "improved C++11 highlighting
Plug 'embear/vim-localvimrc'            "local vimrc
Plug 'ntpeters/vim-better-whitespace'   "highlight and strip trailing whitespace
Plug 'airblade/vim-gitgutter'           "show changed lines in git on margin
Plug 'matze/vim-move'                   "move lines up/down with c-k/c-j
Plug 'rr-/vim-hexdec'                   "convert hex to dec and vice versa
Plug 'junegunn/vim-easy-align'          "replace :column ...
Plug 'bronson/vim-visual-star-search'   "enable * and # in visual mode
Plug 'duggiefresh/vim-easydir'          "create directories on save
Plug 'terryma/vim-multiple-cursors'
call plug#end()

runtime editor.vim
runtime indent.vim
runtime plugins.vim
runtime keyboard.vim
runtime filetypes.vim
runtime theme.vim
