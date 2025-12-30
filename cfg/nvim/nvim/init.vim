call plug#begin()
Plug 'ibhagwan/fzf-lua'                 "open files using fuzzy matching
Plug 'ntpeters/vim-better-whitespace'   "highlight and strip trailing whitespace
Plug 'matze/vim-move'                   "move lines up/down with c-k/c-j
Plug 'rr-/vim-hexdec'                   "convert hex to dec and vice versa
Plug 'junegunn/vim-easy-align'          "replace :column ...
Plug 'bronson/vim-visual-star-search'   "enable * and # in visual mode
Plug 'duggiefresh/vim-easydir'          "create directories on save
Plug 'christoomey/vim-tmux-navigator'   "integration with tmux
Plug 'fisadev/vim-isort'                "sort includes in python source code
Plug 'editorconfig/editorconfig-vim'    "respect .editorconfig
Plug 'Asheq/close-buffers.vim'          "close hidden buffers
Plug 'lambdalisue/fern.vim'             "alternative to buggy and unwieldy netrw
Plug 'lambdalisue/fern-hijack.vim'      "replace netrw
"Plug 'nvim-treesitter/nvim-treesitter', {'branch': 'master', 'do': ':TSUpdate'} "syntax highlighting
Plug 'stevearc/aerial.nvim'

call plug#end()

lua require('editor')
lua require('indent')
runtime plugins.vim
lua require('keyboard')
lua require('other')
lua require('file-types')
lua require('theme')
lua require('syntax')
