"----------------------------------------
"- color scheme settings
"----------------------------------------

" airline
let g:airline_theme = 'ubaryd'
"allow use of special characters that are supplied by terminal font
let g:airline_powerline_fonts = 1

" Remove all existing highlighting and set the defaults.
highlight clear

" Remove all highlighting
highlight clear Constant
highlight clear Number
highlight clear Statement
highlight clear PreProc
highlight clear Type
highlight clear Special
highlight clear Identifier
highlight clear String
highlight clear Comment
highlight clear Error
highlight clear LineNr
highlight clear NonText
highlight clear SpecialKey

highlight String     term=underline cterm=NONE ctermfg=Magenta
highlight Comment    term=bold      cterm=NONE ctermfg=Cyan
highlight Error      term=reverse   cterm=NONE ctermbg=Red
highlight LineNr     term=bold      cterm=NONE ctermfg=238
highlight NonText    term=bold      cterm=NONE ctermfg=Yellow
highlight SpecialKey term=bold      cterm=NONE ctermfg=Yellow
