filetype off
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
call plug#end()

"-------------------------------------------------
" basic settings
"-------------------------------------------------
set synmaxcol=256             "highlight up to X columns (binary files)
set number                    "enable line numbers
set nofoldenable              "disable folding

"fix fast hitting escape + <key> being interpreted as escape sequence
if ! has('gui_running')
    set ttimeoutlen=10
    augroup FastEscape
        autocmd!
        au InsertEnter * set timeoutlen=0
        au InsertLeave * set timeoutlen=1000
    augroup END
endif

"color scheme
if $LIGHTNESS ==? 'light'     "$LIGHTNESS exported by zshrc
  set background=light
  colorscheme hemisu
else
  set background=dark
  colorscheme sorcerer
endif

let g:fzf_nvim_statusline = 0
function! s:fzf_statusline()
  " Override statusline as you like
  setlocal statusline=%#fzf1#\ >\ %#fzf2#fz%#fzf3#f
endfunction

autocmd! User FzfStatusLine call <SID>fzf_statusline()

"set gutter width to 80 characters
if exists('+colorcolumn')
  set colorcolumn=80
endif

"gui specific options
if has('gui_running')
  colorscheme winter
  set guioptions-=m             "remove menu bar
  set guioptions-=T             "remove toolbar
  set guioptions-=r             "remove right-hand scroll bar
  set guioptions-=L             "remove left-hand scroll bar
  set guifont=Liberation\ Mono\ 9
endif

"-----------------------------------------
" whitespace settings
"-----------------------------------------
set enc=utf-8                 "character encoding of gui
set fencs=utf-8,cp932         "preferred character encodings
set ff=unix ffs=unix,dos      "preferred eol styles
set expandtab                 "use spaces instead of tab
set tabstop=4                 "spaces that tab counts for
set softtabstop=4             "spaces that tab counts for in edit mode
set shiftwidth=4              "spaces for each step of auto-indent
set autoindent                "auto indentation
set wrapscan                  "search again from top if no matches
set nowrap                    "don't wrap long lines
set formatoptions-=c          "auto comment continuation works against me
filetype plugin indent off    "auto indentation works against me

"----------------------------------------
" editor behavior
"----------------------------------------
set virtualedit=onemore       "allow moving cursor up to EOL+1 character
set splitbelow splitright     "change placement when splitting a buffer
set shell=/bin/zsh            "when opening shell, use zsh
set noincsearch               "disable "live" search
set ignorecase                "ignore case in searches
set smartcase                 " ...unless they contain uppercase chars
set scrolloff=5               "keep at least x lines below and above cursor
set nojoinspaces              "don't put double spaces when using auto wrapping
set fillchars=vert:\│         "better character for vertical window splits
set hidden                    "don't purge undo history when changing buffers

"----------------------------------------
" miscellaneous
"----------------------------------------
set noeb vb t_vb=             "disable beeping
set laststatus=2              "always display status line
set modeline                  "allow files to embed file-specific vim settings
set modelines=5               " ...within X lines at the top of that file
set nospell                   "spell checker is off by default
set spelllang=en_us,pl        "spell checker languages
set spellfile=~/.config/nvim/spell/en.utf-8.add,~/.config/nvim/spell/pl.utf-8.add

"------------------------------------------
" storage
"------------------------------------------
"double slash prevents file name collision, by using full file paths
set viminfo+=n~/.config/nvim/viminfo  "set path to last session data storage
set backupdir=~/.config/nvim/backup// "set path to file backups
set backup                            "enable backups
set directory=~/.config/nvim/swap//   "set path to swap files (.*.swp)
set undodir=~/.config/nvim/undo//     "set path to undo data file
set undofile
set undolevels=1000
set undoreload=10000

"------------------------------------------
" ignore files in commands and plugins
"------------------------------------------
"list of files to ignore
set wildignore+=.hg,.git,.bzr
set wildignore+=*.o,*.obj
set wildignore+=*.pyc,*.pyo,__pycache__
set wildignore+=*.swp,*.spl
set wildignore+=*.stackdump
set wildignore+=*~.*
set wildignorecase "case-insensitive filename completion in commands

"----------------------------------------
" highlight bad whitespace
"----------------------------------------
"highlight color for bad whitespace
highlight SpecialKey ctermbg=NONE ctermfg=187
"fix ColorColumn on dark backgrounds
if &background == 'dark'
  highlight ColorColumn ctermbg=235
else
  highlight Normal ctermbg=NONE
  highlight ColorColumn ctermbg=255 guibg=#ddaaaa
end
"show white characters
set list listchars=tab:→\ ,trail:·

"----------------------------------------
" custom commands
"----------------------------------------
"fast indentation styles for working with other people's projects
command! TwoSpaces set et sts=2 ts=2 sw=2
command! FourSpaces set et sts=4 ts=4 sw=4
command! Tabs set noet sts=4 ts=4 sw=4

"----------------------------------------
" config localvimrc
"----------------------------------------
let g:localvimrc_persistent = 1         "remember decisions to load given lvimrc

"----------------------------------------
" config vim-move
"----------------------------------------
let g:move_key_modifier = 'C'           "c-j and c-k rather than default binding
let g:move_auto_indent = 0              "disable indentation aids

"----------------------------------------
" config airline
"----------------------------------------
"because of white background
if &background == 'dark'
  let g:airline_theme = 'ubaryd'
else
  let g:airline_theme = 'sol'
endif
"allow use of special characters that are supplied by terminal font
let g:airline_powerline_fonts = 1

"----------------------------------------
" config gitgutter
"----------------------------------------
let g:gitgutter_sign_column_always = 1
set updatetime=250

"----------------------------------------
" config NERDtree
"----------------------------------------
"f2 = disable NERDtree
autocmd VimEnter * inoremap <F2> <esc>:NERDTreeToggle<CR>
autocmd VimEnter * nnoremap <F2> :NERDTreeToggle<CR>
"f3 = find current file in nerdtree
autocmd VimEnter * inoremap <F3> <esc>:NERDTreeFind<CR>
autocmd VimEnter * nnoremap <F3> :NERDTreeFind<CR>
"explicitly disable some things in NERDTree - seems like wildignore glitches
let NERDTreeIgnore=['__pycache__','vendor','build/']

"----------------------------------------
" file-type specific settings
"----------------------------------------

"correct .lst filetype from assembler to text
autocmd BufRead,BufNewFile *.lst set filetype=text

"strip trailing whitespace for common source code
autocmd FileType c,cc,cxx,cpp,h,hpp,java,php,python,ruby,vim
  \ autocmd BufWritePre <buffer> :StripWhitespace

"enable spellcheck and hard wrapping for text files
autocmd FileType text,markdown setlocal spell textwidth=79

"enable spellcheck and double gutter in git commit messages
autocmd FileType gitcommit setlocal spell textwidth=72 colorcolumn=50,72

"disable syntax for certain files
autocmd FileType text,xml,json setlocal syntax=

"setup indentation for common file types
autocmd FileType text     FourSpaces
autocmd FileType plaintex FourSpaces
autocmd FileType markdown FourSpaces
autocmd FileType c        FourSpaces
autocmd FileType cpp      FourSpaces
autocmd FileType python   FourSpaces
autocmd FileType lua      FourSpaces
autocmd FileType ruby     TwoSpaces
autocmd FileType vim      TwoSpaces
autocmd FileType zsh      FourSpaces
autocmd FileType sh       FourSpaces
autocmd FileType make     Tabs
autocmd FileType php      FourSpaces
autocmd FileType js       FourSpaces
autocmd FileType css      FourSpaces

"automatically sort word lists and generate spell files
autocmd BufWritePre */spell/*.add %sort i
autocmd BufWritePost */spell/*.add silent mkspell! %

"----------------------------------------
" custom keyboard bindings
"----------------------------------------
"set the leader key to -
let mapleader = "-"
"movement over visual lines, not physical lines
map <buffer> <silent> k gk
map <buffer> <silent> j gj
"ctrl+s = save
inoremap <silent> <C-s> <Esc>:update<CR>
nnoremap <silent> <C-s> :<C-u>update<CR>
"ctrl+z = open shell
nnoremap <silent> <C-z> :te<CR>
"ctrl+q = close window
inoremap <silent> <C-q> <Esc>:q<CR>
nnoremap <silent> <C-q> :q<CR>
"ctrl+w ctrl+m = open new file vertically
nnoremap <silent> <C-w><C-m> :vne<CR>
nnoremap <silent> <C-w>m :vne<CR>
"make motion search easier to access
nmap <leader>z <Plug>(easymotion-s)
"save with sudo
cnoremap w!! w !sudo tee >/dev/null %
"disable stupid manual pages
nnoremap <silent> <S-K> <nop>
vnoremap <silent> <S-K> <nop>
"easier formatting of paragraphs
vnoremap Q gq
nnoremap Q gqap

  "----------------------------------------
  " interchange command-t and ctrl-p
  "----------------------------------------
  nnoremap <C-p> :Files<CR>
  nnoremap <C-m> :Buffers<CR>
