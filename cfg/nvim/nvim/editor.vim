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
set relativenumber            "show relative line numbers

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
set nowrap                    "don't wrap long lines
set linebreak                 "wrap lines at word boundaries

"automatic aids
set formatoptions-=t          "disable autowrapping text
set formatoptions-=c          "disable autowrapping comments
set formatoptions-=r          "disable inserting comment prefix after <Enter>
set formatoptions-=o          "disable inserting comment prefix after 'o'/'O'
set formatoptions-=j          "keep the comment prefix when joining lines
"respect my choice even for ftplugin
autocmd FileType * setlocal fo-=t fo-=c fo-=r fo-=o fo-=j

"editor behavior
set showcmd                   "show last command in status
set virtualedit=onemore       "allow moving cursor up to EOL+1 character
set splitbelow splitright     "change placement when splitting a buffer
set shell=/bin/zsh            "when opening shell, use zsh
set wrapscan                  "search again from top if no matches
set noincsearch               "disable 'live' search
set ignorecase                "ignore case in searches
set smartcase                 " ...unless they contain uppercase chars
set scrolloff=5               "keep at least x lines below and above cursor
set nojoinspaces              "don't put double spaces when using auto wrapping
set fillchars=vert:\│         "better character for vertical window splits
set hidden                    "don't purge undo history when changing buffers
set clipboard+=unnamed        "automatically copy unnamed yanks to "*
set clipboard+=unnamedplus    "automatically copy unnamed yanks to "+

"miscellaneous
set noeb vb t_vb=             "disable beeping
set laststatus=2              "always display status line
set modeline                  "allow files to embed file-specific vim settings
set modelines=1               " ...within X lines at the top of that file

"spellcheck
set nospell                   "spell checker is off by default
set spelllang=en_us,pl        "spell checker languages
let &spellfile=
  \$HOME.'/.config/'.s:dir.'/spell/en.utf-8.add,'.
  \$HOME.'/.config/'.s:dir.'/spell/pl.utf-8.add'

"folds
set nofoldenable              "disable folding
set foldopen-=block           "{ and } skips over folds
set foldmethod=indent         "fold basing on indent (to be used with zM / zR)
set foldnestmax=2             "don't fold too deep

"storage
"double slash prevents file name collision, by using full file paths
set backup            "enable backups
set undofile          "enable persistent undo
set undolevels=1000   "store this many undo levels
set undoreload=10000  "don't wipe undo after reloading file up to 10k lines long
let &backupdir=$HOME.'/.local/share/nvim/backup//' "path to file backups

"ignore files in commands and plugins
set wildignore+=.hg,.git,.bzr
set wildignore+=*.o,*.obj
set wildignore+=*.pyc,*.pyo,__pycache__
set wildignore+=*.swp,*.spl
set wildignore+=*.stackdump
set wildignore+=*~.*
set wildignorecase    "case-insensitive filename completion in commands
