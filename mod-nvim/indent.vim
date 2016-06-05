"----------------------------------------
"- indentation settings
"----------------------------------------

set expandtab                 "use spaces instead of tab
set tabstop=4                 "spaces that tab counts for
set softtabstop=4             "spaces that tab counts for in edit mode
set shiftwidth=4              "spaces for each step of auto-indent

"fast indentation styles for working with other people's projects
command! TwoSpaces set et sts=2 ts=2 sw=2
command! FourSpaces set et sts=4 ts=4 sw=4
command! Tabs set noet sts=4 ts=4 sw=4

set autoindent                "match indentation from previous line after <CR>
set nosmartindent             "don't add any extra indenation after { (I)
set nocindent                 "don't add any extra indenation after { (II)
filetype plugin indent off    "auto indentation works against me

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
