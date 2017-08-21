call plug#begin()
Plug 'junegunn/fzf', { 'dir': '~/.fzf', 'do': './install --all' }
Plug 'junegunn/fzf.vim'                 "open files using fuzzy matching
Plug 'Lokaltog/vim-easymotion'          "move to any character!
Plug 'Yggdroot/indentLine'              "vertical bars showing indent level
Plug 'ntpeters/vim-better-whitespace'   "highlight and strip trailing whitespace
Plug 'airblade/vim-gitgutter'           "show changed lines in git on margin
Plug 'matze/vim-move'                   "move lines up/down with c-k/c-j
Plug 'rr-/vim-hexdec'                   "convert hex to dec and vice versa
Plug 'junegunn/vim-easy-align'          "replace :column ...
Plug 'bronson/vim-visual-star-search'   "enable * and # in visual mode
Plug 'duggiefresh/vim-easydir'          "create directories on save
Plug 'christoomey/vim-tmux-navigator'   "integration with tmux
Plug 'tpope/vim-vinegar'                "better tpope
call plug#end()

runtime editor.vim
runtime indent.vim
runtime plugins.vim
runtime keyboard.vim
runtime filetypes.vim
runtime theme.vim
runtime gui.vim
