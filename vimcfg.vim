runtime bundle/pathogen/autoload/pathogen.vim
execute pathogen#infect()

syntax on
set virtualedit=onemore
set number
"show white characters
set list listchars=tab:→\ ,trail:·
"set terminal to 256 color
if $TERM == "xterm" || $TERM == "xterm-256color" || $TERM == "screen" || $TERM == "screen-256color" || $COLORTERM == "gnome-terminal"
	set t_Co=256
endif

"disable .vimrc in Windows
if has('win32') || has('win64') || has('win32unix')
	set viminfo="NONE"
endif

"color scheme
set background=light
colorscheme hemisu

"highlight whitespace
highlight SpecialKey ctermbg=NONE ctermfg=187
"highlight trailing white space
highlight ExtraWhitespace ctermbg=red guibg=red
"highlight searches
highlight IncSearch ctermfg=black ctermbg=yellow

"set gutter width to 80 characters
if exists('+colorcolumn')
	set colorcolumn=80
endif

"match trailing spaces and spaces before a tab
autocmd BufWinEnter * match ExtraWhitespace /\s\+$\|\s* \+\t\+\|\s*\t\+ \+/



"case insensitive filename completion in normal mode
set wildignorecase
"don't use spaces instead of tab
set noexpandtab
"number of spaces that tab counts for
set tabstop=4
"number of spaces that tab counts for while editing
set softtabstop=4
"number of spaces for each step of auto-indent
set shiftwidth=4
"auto indentation
set autoindent
"disable auto indentation based on file types
filetype indent off


set nowrap
"allow backspacing over indent, eol and ?
set bs=indent,eol,start
"arrows over visible lines, not physical lines
noremap  <buffer> <silent> <Up>   gk
noremap  <buffer> <silent> <Down> gj
noremap  <buffer> <silent> <Home> g<Home>
noremap  <buffer> <silent> <End>  g<End>
inoremap <buffer> <silent> <Up>   <C-o>gk
inoremap <buffer> <silent> <Down> <C-o>gj
inoremap <buffer> <silent> <Home> <C-o>g<Home>
inoremap <buffer> <silent> <End>  <C-o>g<End>


"change cursor buffer position in newly split buffers
set splitbelow splitright
"disable beeping
set noeb vb t_vb=
"always display status line
set laststatus=2


set ff=unix ffs=unix,dos
set enc=utf-8 fileencoding=utf-8
"disable making "file~"
set nobackup
"disallow files to embed vim settings
set nomodeline

"disable "live" search
set noincsearch
"highlight searches
set hlsearch
"ignore case in searches unless they contain uppercase characters
set ignorecase
set smartcase

"enable mouse support
set mouse=a
"setup spell checker
set nospell
set spelllang=en_us,pl


"ctrl+t = new tab
:nmap <C-t> :tabnew<CR>
:imap <C-t> <Esc>:tabnew<CR>


"config ctrl+p
let g:ctrlp_custom_ignore = {}
let g:ctrlp_custom_ignore.dir  = '\v'
"folders: cvs general
let g:ctrlp_custom_ignore.dir .= '\.hg|\.git|\.bzr'
"folders: 'data'
let g:ctrlp_custom_ignore.dir .= '|data'
"folders: pinkyard
let g:ctrlp_custom_ignore.dir .= '|files|thumbs'
"folders: 'library/Zend'
let g:ctrlp_custom_ignore.dir .= '|library[/\\]Zend'
"folders: subfolders of luna:/cygdrive/z
let g:ctrlp_custom_ignore.dir .= '|\.dl|\.ul|archive|img|software|video'
let g:ctrlp_custom_ignore.file  = '\v'
"backups
let g:ctrlp_custom_ignore.file .= '\~$'
let g:ctrlp_custom_ignore.file .= '|\.('
"extensions: programming rubbish files
let g:ctrlp_custom_ignore.file .= 'o|swp|pyc|svn-base'
"extensions: archives
let g:ctrlp_custom_ignore.file .= '|tar|zip|7z|gz'
"extensions: images
let g:ctrlp_custom_ignore.file .= '|jpg|jpeg|gif|png|tga|bmp'
"extensions: documents
let g:ctrlp_custom_ignore.file .= '|pdf|doc|xls'
"extensions: multimedia
let g:ctrlp_custom_ignore.file .= '|wav|ogg|mp3|mp4|avi|mkv|ttf'
let g:ctrlp_custom_ignore.file .= ')$'
"disable CWD bullshit
let g:ctrlp_working_path_mode = 0
"enable .htaccess etc
let g:ctrlp_dotfiles = 1
"show selected element at the top
let g:ctrlp_match_window_bottom = 1
"show list top->bottom
let g:ctrlp_match_window_reversed = 1


"enable rainbow parentheses
let g:rainbow_active = 1


"enable on console startup
let g:nerdtree_tabs_open_on_console_startup = 1
"always focus on files
let g:nerdtree_tabs_focus_on_files = 1
"don't focus nerdtree on parameterless startup
let g:nerdtree_tabs_smart_startup_focus = 2
"f3 = find current file in nerdtree
autocmd VimEnter * imap <F3> <esc>:NERDTreeFind<CR>
autocmd VimEnter * nmap <F3> :NERDTreeFind<CR>


"file type specific settings
autocmd BufRead,BufNewFile *.txt,*.tex setlocal spell expandtab textwidth=79
autocmd BufRead,BufNewFile *.lst setlocal expandtab
autocmd BufRead,BufNewFile *.php,*.phtml call SetPhpOptions()

function SetPhpOptions()
	if exists('+colorcolumn')
		setlocal cc=120
	endif
	setlocal tw=119
endfunction


function! ReloadConfig()
	source $MYVIMRC
endfunction
