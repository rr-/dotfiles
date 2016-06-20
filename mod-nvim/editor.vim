"-------------------------------------------------
"- basic settings
"-------------------------------------------------

if has('nvim')
  let s:dir='nvim'
else
  let s:dir='vim'
endif

syntax on                     "enable syntax highlighting
set synmaxcol=256             "highlight up to X columns (binary files)
set number                    "enable line numbers
set nofoldenable              "disable folding

"fix fast hitting escape + <key> being interpreted as escape sequence
if !has('gui_running')
  set ttimeout
  set ttimeoutlen=10
  augroup FastEscape
    autocmd!
    au InsertEnter * set timeoutlen=0
    au InsertLeave * set timeoutlen=1000
  augroup END
endif

"highlight color for bad whitespace
highlight SpecialKey ctermbg=NONE ctermfg=187
"show white characters
set list listchars=tab:→\ ,trail:·

"set gutter width to 80 characters
if exists('+colorcolumn')
  set colorcolumn=80
endif

"whitespace settings
set enc=utf-8                 "character encoding of ui
set fencs=utf-8,cp932         "preferred character encodings
set ff=unix ffs=unix,dos      "preferred eol styles
set wrapscan                  "search again from top if no matches
set nowrap                    "don't wrap long lines
set formatoptions-=c          "auto comment continuation works against me

"editor behavior
set virtualedit=onemore       "allow moving cursor up to EOL+1 character
set splitbelow splitright     "change placement when splitting a buffer
set shell=/bin/zsh            "when opening shell, use zsh
set noincsearch               "disable 'live' search
set ignorecase                "ignore case in searches
set smartcase                 " ...unless they contain uppercase chars
set scrolloff=5               "keep at least x lines below and above cursor
set nojoinspaces              "don't put double spaces when using auto wrapping
set fillchars=vert:\│         "better character for vertical window splits
set hidden                    "don't purge undo history when changing buffers

"miscellaneous
set noeb vb t_vb=             "disable beeping
set laststatus=2              "always display status line
set modeline                  "allow files to embed file-specific vim settings
set modelines=5               " ...within X lines at the top of that file
set nospell                   "spell checker is off by default
set spelllang=en_us,pl        "spell checker languages
let &spellfile=
  \$HOME.'/.config/'.s:dir.'/spell/en.utf-8.add,'.
  \$HOME.'/.config/'.s:dir.'/spell/pl.utf-8.add'

"folds
set foldopen-=block           "{ and } skips over folds
set foldmethod=indent         "fold basing on indent (to be used with zM / zR)
set foldnestmax=2             "don't fold too deep

"storage
"double slash prevents file name collision, by using full file paths
set backup            "enable backups
set undofile          "enable persistent undo
set undolevels=1000   "store this many undo levels
set undoreload=10000  "don't wipe undo after reloading file up to 10k lines long
let &viminfo=$HOME.'/.config/'.s:dir.'/viminfo'    "path to session storage
let &backupdir=$HOME.'/.config/'.s:dir.'/backup//' "path to file backups
let &directory=$HOME.'/.config/'.s:dir.'/swap//'   "path to swap files (.*.swp)
let &undodir=$HOME.'/.config/'.s:dir.'/undo//'     "path to undo data

"ignore files in commands and plugins
set wildignore+=.hg,.git,.bzr
set wildignore+=*.o,*.obj
set wildignore+=*.pyc,*.pyo,__pycache__
set wildignore+=*.swp,*.spl
set wildignore+=*.stackdump
set wildignore+=*~.*
set wildignorecase    "case-insensitive filename completion in commands

function! DeleteHiddenBuffers()
    redir => buffersoutput
    buffers
    redir END
    let buflist = split(buffersoutput,"\n")
    for item in filter(buflist,"v:val[5] == 'h'")
            exec 'bdelete ' . item[:2]
    endfor
endfunction
command! DeleteHiddenBuffers call DeleteHiddenBuffers()
