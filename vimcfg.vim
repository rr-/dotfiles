runtime bundle/pathogen/autoload/pathogen.vim
execute pathogen#infect()

syntax on                                     " syntax coloring
set ff=unix ffs=unix,dos                      " use unix line endings in new files; prefer unix line endings
set enc=utf-8 fileencoding=utf-8              " text encoding; second command probably makes no sense
set nobackup                                  " disable making "file~"
set splitbelow splitright                     " change cursor buffer position in newly splitted buffers
set noeb vb t_vb=                             " disable beeping
set guifont=Lucida\ Console:h10:cEASTEUROPE   " set font for graphical vim
set laststatus=2                              " always display status line
set nowrap                                    " don't wrap text
set bs=indent,eol,start                       " allow backspacing over indent, eol and ?
set noexpandtab                               " don't use spaces instead of tab
set tabstop=4                                 " number of spaces that tab counts for
set softtabstop=4                             " number of spaces that tab counts for while editing
set shiftwidth=4                              " number of spaces for each steo of autoindent
set autoindent                                " auto indentation
filetype indent off                           " disable auto indentation based on file types
set list listchars=tab:→\ ,trail:·            " show white characters
set noincsearch                               " disable "live" search
set hlsearch                                  " highlight searches
set ignorecase smartcase                      " ignore case in searches, but don't ignore case in searches if they contain uppercase characters
set number                                    " turn on line numbers
set mouse=a                                   " enable mouse suppor
set spell spelllang=en_us                     " enable spell checker
set nomodeline                                " disallow files to embed vim settings

" color scheme
let g:solarized_termcolors=256
set background=light
colorscheme solarized

" set terminal to 256 color
if $TERM == "xterm" || $TERM == "xterm-256color" || $TERM == "screen-256color" || $COLORTERM == "gnome-terminal"
	set t_Co=256
endif

" various highlights
highlight SpecialKey ctermbg=NONE ctermfg=187                 " whitespace
highlight ExtraWhitespace ctermbg=red guibg=red               " trailing white space
highlight OverLength ctermbg=red ctermfg=white guibg=#592929
autocmd BufWinEnter * set cc=80
" match trailing spaces and spaces before a tab
autocmd BufWinEnter * match ExtraWhitespace /\s\+$\|\s* \+\t\+\|\s*\t\+ \+/

" ctrl+t = new tab
:nmap <C-t> :tabnew<CR>
:imap <C-t> <Esc>:tabnew<CR>



" config ctrl+p
let g:ctrlp_custom_ignore = {}
let g:ctrlp_custom_ignore.dir  = '\v'
let g:ctrlp_custom_ignore.dir .= '\.hg|\.git|\.bzr'              " folders: cvs general
let g:ctrlp_custom_ignore.dir .= '|data'                         " folders: 'data'
let g:ctrlp_custom_ignore.dir .= '|files|thumbs'                 " folders: pinkyard
let g:ctrlp_custom_ignore.dir .= '|library[/\\]Zend'             " folders: 'library/Zend'
let g:ctrlp_custom_ignore.dir .= '|\.dl|\.ul|archive|img|software|video'  " folders: subfolders of luna:/cygdrive/z
let g:ctrlp_custom_ignore.file  = '\v'
let g:ctrlp_custom_ignore.file .= '\~$'                          " backups
let g:ctrlp_custom_ignore.file .= '|\.('
let g:ctrlp_custom_ignore.file .= 'o|swp|pyc|svn-base'           " extensions: programming rubbish files
let g:ctrlp_custom_ignore.file .= '|tar|zip|7z|gz'               " extensions: archives
let g:ctrlp_custom_ignore.file .= '|jpg|jpeg|gif|png|tga|bmp'    " extensions: images
let g:ctrlp_custom_ignore.file .= '|pdf|doc|xls'                 " extensions: documents
let g:ctrlp_custom_ignore.file .= '|wav|ogg|mp3|mp4|avi|mkv|ttf' " extensions: multimedia
let g:ctrlp_custom_ignore.file .= ')$'
let g:ctrlp_working_path_mode = 0     " disable CWD bullshit
let g:ctrlp_dotfiles = 1              " enable .htaccess etc
let g:ctrlp_match_window_bottom = 1   " show selected element at the top
let g:ctrlp_match_window_reversed = 1 " show list top->bottom



" config vim-nerdtree-tabs
let g:nerdtree_tabs_open_on_console_startup = 1 " enable on console startup
let g:nerdtree_tabs_focus_on_files = 1          " always focus on files
let g:nerdtree_tabs_smart_startup_focus = 2     " don't focus nerdtree on parameterless startup
" f3 d toggle nerdtree
"autocmd VimEnter * imap <F3> <esc>:NERDTreeSteppedOpen<CR>
"autocmd VimEnter * nmap <F3> :NERDTreeSteppedOpen<CR>
" f3 = find current file in nerdtree
autocmd VimEnter * imap <F3> <esc>:NERDTreeFind<CR>
autocmd VimEnter * nmap <F3> :NERDTreeFind<CR>



" arrows over visible lines, not physical lines
noremap  <buffer> <silent> <Up>   gk
noremap  <buffer> <silent> <Down> gj
noremap  <buffer> <silent> <Home> g<Home>
noremap  <buffer> <silent> <End>  g<End>
inoremap <buffer> <silent> <Up>   <C-o>gk
inoremap <buffer> <silent> <Down> <C-o>gj
inoremap <buffer> <silent> <Home> <C-o>g<Home>
inoremap <buffer> <silent> <End>  <C-o>g<End>



function! ReloadConfig()
	source $MYVIMRC
endfunction
