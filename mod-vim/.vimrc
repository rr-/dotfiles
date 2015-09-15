set nocompatible
filetype off
set rtp+=~/.vim/vundle/
call vundle#begin()
Plugin 'gmarik/Vundle.vim'                "better plugin manager
Plugin 'kien/ctrlp.vim'                   "open files using fuzzy matching
Plugin 'scrooloose/nerdtree'              "file explorer sidebar
Plugin 'Lokaltog/vim-easymotion'          "move to any character!
Plugin 'bling/vim-airline'                "riced status bar
Plugin 'Yggdroot/indentLine'              "vertical bars showing indent level
Plugin 'flazz/vim-colorschemes'           "color schemes!
Plugin 'maxbrunsfeld/vim-yankstack'       "enhanced yank/paste stack
Plugin 'octol/vim-cpp-enhanced-highlight' "improved C++11 highlighting
call vundle#end()

"-------------------------------------------------
" basic settings
"-------------------------------------------------
syntax on                     "enable syntax highlighting
set synmaxcol=256             "highlight up to X columns (binary files)
set number                    "enable line numbers

"set terminal to 256 color
if $TERM == "xterm"
\ || $TERM == "xterm-256color"
\ || $TERM == "fbterm"
\ || $TERM == "screen"
\ || $TERM == "screen-256color"
\ || $TERM == "rxvt-unicode-256color"
  set t_Co=256
endif

"color scheme
let background_file=$HOME."/.vimrc-background"
if filereadable(background_file)
  exec 'so ' . background_file
else
  colorscheme hemisu
  set background=light
endif

"set gutter width to 80 characters
if exists('+colorcolumn')
  set colorcolumn=80
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
filetype on                   "enable setting options based on file

"----------------------------------------
" editor behavior
"----------------------------------------
set bs=indent,eol,start       "allow backspacing over indent, eol and ?
set virtualedit=onemore       "allow moving cursor up to EOL+1 character
set wildignorecase            "case-insensitive filename completion in commands
set splitbelow splitright     "change placement when splitting a buffer
set shell=/bin/zsh            "when opening shell, use zsh
set mouse=a                   "enable mouse support
set noincsearch               "disable "live" search
set hlsearch                  "highlight searches
set ignorecase                "ignore case in searches
set smartcase                 " ...unless they contain uppercase chars
set scrolloff=10              "keep at least 10 lines below and above cursor
set nojoinspaces              "don't put double spaces when using auto wrapping
set fillchars=vert:\│         "better vertical fill character

"----------------------------------------
" miscellaneous
"----------------------------------------
set noeb vb t_vb=             "disable beeping
set laststatus=2              "always display status line
set modeline                  "allow files to embed file-specific vim settings
set modelines=5               " ...within X lines at the top of that file
set nospell                   "spell checker is off by default
set spelllang=en_us,pl        "spell checker languages
set spellfile=~/.vim/spell/en.utf-8.add,~/.vim/spell/pl.utf-8.add

"------------------------------------------
" storage
"------------------------------------------
"double slash prevents file name collision, by using full file paths
set viminfo+=n~/.vim/viminfo       "set path to last session data storage
set backupdir=~/.vim/backup//      "set path to file backups
set backup                         "enable backups
set directory=~/.vim/swap//        "set path to swap files (.*.swp)
set undodir=~/.vim/undo//          "set path to undo data file

"----------------------------------------
" highlight bad whitespace
"----------------------------------------
"highlight color for bad whitespace
highlight SpecialKey ctermbg=NONE ctermfg=187
"highlight trailing white space
highlight ExtraWhitespace ctermbg=red guibg=red
"fix ColorColumn on dark backgrounds
if &background == 'dark'
  highlight ColorColumn ctermbg=233
else
  highlight Normal ctermbg=NONE
  highlight ColorColumn ctermbg=255
end
"show white characters
set list listchars=tab:→\ ,trail:·
"match trailing spaces and spaces before a tab
autocmd BufWinEnter * match ExtraWhitespace /\v\s+$|\t+ ([^*]|$)| \t+/

"----------------------------------------
" custom commands
"----------------------------------------
"fast indentation styles for working with other people's projects
command! TwoSpaces set et sts=2 ts=2 sw=2
command! FourSpaces set et sts=4 ts=4 sw=4
command! Tabs set noet sts=4 ts=4 sw=4
"create working dirs for current file
command! CreateDirs execute ':silent !mkdir -p %:h' | write | redraw!
"copy text file with hard wraps (e.g. Markdown) as one line
function! CopyWithoutHardWrapping()
  let old_tw=&textwidth
  :set tw=10000
  silent! normal gg gqG
  silent! normal gg "*yG
  let &textwidth=old_tw
  undo
endfunction
command! CopyWithoutHardWrapping call CopyWithoutHardWrapping()

"close all inactive buffers (tabs + ctrl+p + splitscreen ftw)
function! DeleteInactiveBufs()
  let tablist = []
  for i in range(tabpagenr('$'))
    call extend(tablist, tabpagebuflist(i + 1))
  endfor

  let nWipeouts = 0
  for i in range(1, bufnr('$'))
    if bufexists(i) && !getbufvar(i,"&mod") && index(tablist, i) == -1
      silent exec 'bwipeout' i
      let nWipeouts = nWipeouts + 1
    endif
  endfor
  echomsg nWipeouts . ' buffer(s) wiped out'
endfunction
command! Bdi :call DeleteInactiveBufs()

"----------------------------------------
" config Ctrl+P
"----------------------------------------
"try to open Ctrl+P in a directory containing common VCS directories
let g:ctrlp_working_path_mode = 'rc'
"enable matching files such as .htaccess
let g:ctrlp_dotfiles = 1
"show selected element at the top
let g:ctrlp_match_window_bottom = 1
"show list top->bottom
let g:ctrlp_match_window_reversed = 1
let g:ctrlp_by_filename = 1
let g:ctrlp_match_window = 'bottom,order:btt,min:1,max:10,results:10'
"ignored files and directories
let g:ctrlp_custom_ignore = {}
let g:ctrlp_custom_ignore.dir  = '\v(^|\/)('
let g:ctrlp_custom_ignore.dir .= '\.hg|\.git|\.bzr'
let g:ctrlp_custom_ignore.dir .= '|data\/posts|_site|files|thumbs'
let g:ctrlp_custom_ignore.dir .= '|vendor|node_modules'
let g:ctrlp_custom_ignore.dir .= ')($|\/)'
let g:ctrlp_custom_ignore.file  = '\v'
let g:ctrlp_custom_ignore.file .= '\~$'
let g:ctrlp_custom_ignore.file .= '|\.('
let g:ctrlp_custom_ignore.file .= 'o|exe|dll|so|o|swp|pyc|svn-base|stackdump'
let g:ctrlp_custom_ignore.file .= '|tar|zip|7z|gz'
let g:ctrlp_custom_ignore.file .= '|jpg|jpeg|gif|png|tga|bmp'
let g:ctrlp_custom_ignore.file .= '|pdf|doc|xls'
let g:ctrlp_custom_ignore.file .= '|wav|ogg|mp3|mp4|avi|mkv|ttf'
let g:ctrlp_custom_ignore.file .= ')$'

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
"enable tabs
let g:airline#extensions#tabline#enabled = 1
"don't show buffers in the tabline - show tabs instead
let g:airline#extensions#tabline#show_buffers = 0
"show tab number near tab for easy navigation with :![number]gt
let g:airline#extensions#tabline#tab_nr_type = 1

"----------------------------------------
" config NERDtree
"----------------------------------------
"disable on console startup
let g:nerdtree_tabs_open_on_console_startup = 0
"always focus on files
let g:nerdtree_tabs_focus_on_files = 1
"don't focus nerdtree on parameterless startup
let g:nerdtree_tabs_smart_startup_focus = 2
"don't display these kinds of files
let NERDTreeIgnore=['\.pyc$', '\.pyo$', '\.obj$', '\.o$']
"f2 = disable NERDtree
autocmd VimEnter * imap <F2> <esc>:NERDTreeToggle<CR>
autocmd VimEnter * nmap <F2> :NERDTreeToggle<CR>
"f3 = find current file in nerdtree
autocmd VimEnter * imap <F3> <esc>:NERDTreeFind<CR>
autocmd VimEnter * nmap <F3> :NERDTreeFind<CR>

"----------------------------------------
" file-type specific settings
"----------------------------------------

"correct .lst filetype from assembler to text
autocmd BufRead,BufNewFile *.lst set filetype=text

"strip trailing whitespace for common source code
autocmd FileType c,cc,cxx,cpp,h,hpp,java,php,python,ruby,vim autocmd BufWritePre <buffer> :%s/\s\+$//e

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
autocmd FileType ruby     TwoSpaces
autocmd FileType vim      TwoSpaces
autocmd FileType zsh      FourSpaces
autocmd FileType sh       FourSpaces
autocmd FileType make     Tabs
autocmd FileType php      FourSpaces
autocmd FileType js       FourSpaces
autocmd FileType css      FourSpaces

"----------------------------------------
" custom keyboard bindings
"----------------------------------------
"set the leader key to -
let mapleader = "-"
"movement over visual lines, not physical lines
map <buffer> <silent> k gk
map <buffer> <silent> j gj
"ctrl+tab, ctrl+shift+tab = move to next/prev tab
nmap <Esc>[1;5I gt<CR>
nmap <Esc>[1;6I gT<CR>
"ctrl+t = open new tab
imap <silent> <C-t> <Esc>:tabnew<CR>
nmap <silent> <C-t> :tabnew<CR>
"ctrl+s = save
imap <silent> <C-s> <Esc>:update<CR>
nmap <silent> <C-s> :<C-u>update<CR>
"ctrl+z = open shell
nmap <silent> <C-z> :sh<CR>
"ctrl+q = close window
imap <silent> <C-q> <Esc>:q<CR>
nmap <silent> <C-q> :q<CR>
"ctrl+o = open Ctrl+P prompt
nmap <silent> <C-o> :CtrlPLine<CR>
"f4 = copy current file path to system clipboard
map <silent> <F4> :let @" = expand("%")<CR>
"make motion search easier to access
nmap <leader>z <leader><leader>s
"access to recent yank/paste stack
nmap <leader>p <Plug>yankstack_substitute_older_paste
nmap <leader>P <Plug>yankstack_substitute_newer_paste
"save with sudo
cmap w!! w !sudo tee >/dev/null %
"arrows are not needed in hhkb :^)
map <Up> <Nop>
map <Down> <Nop>
map <Left> <Nop>
map <Right> <Nop>
imap <Up> <Nop>
imap <Down> <Nop>
imap <Left> <Nop>
imap <Right> <Nop>
"disable stupid manual pages
nmap <silent> <S-K> <nop>

  "----------------------------------------
  " ctrl+k/j = move line up/down
  "----------------------------------------
  function! MoveLineUp()
    call MoveLineOrVisualUp(".", "")
  endfunction

  function! MoveLineDown()
    call MoveLineOrVisualDown(".", "")
  endfunction

  function! MoveVisualUp()
    call MoveLineOrVisualUp("'<", "'<,'>")
    normal gv
  endfunction

  function! MoveVisualDown()
    call MoveLineOrVisualDown("'>", "'<,'>")
    normal gv
  endfunction

  function! MoveLineOrVisualUp(line_getter, range)
    let l_num = line(a:line_getter)
    if l_num - v:count1 - 1 < 0
        let move_arg = "0"
    else
        let move_arg = a:line_getter." -".(v:count1 + 1)
    endif
    call MoveLineOrVisualUpOrDown(a:range."move ".move_arg)
  endfunction

  function! MoveLineOrVisualDown(line_getter, range)
    let l_num = line(a:line_getter)
    if l_num + v:count1 > line("$")
        let move_arg = "$"
    else
        let move_arg = a:line_getter." +".v:count1
    endif
    call MoveLineOrVisualUpOrDown(a:range."move ".move_arg)
  endfunction

  function! MoveLineOrVisualUpOrDown(move_arg)
    let col_num = virtcol(".")
    execute "silent! ".a:move_arg
    execute "normal! ".col_num."|"
  endfunction

  nnoremap <silent> <C-k> :<C-u>call MoveLineUp()<CR>
  nnoremap <silent> <C-j> :<C-u>call MoveLineDown()<CR>
  vnoremap <silent> <C-k> :<C-u>call MoveVisualUp()<CR>
  vnoremap <silent> <C-j> :<C-u>call MoveVisualDown()<CR>
  inoremap <silent> <C-k> <Esc>:call MoveLineUp()<CR>a
  inoremap <silent> <C-j> <Esc>:call MoveLineDown()<CR>a
