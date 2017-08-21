"----------------------------------------
"- color scheme settings
"----------------------------------------

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
highlight StatusLine term=bold      cterm=NONE ctermbg=234

"highlight color for bad whitespace
highlight SpecialKey ctermbg=NONE ctermfg=167
highlight ColorColumn ctermbg=52

highlight SpellBad ctermbg=52
highlight VertSplit cterm=NONE ctermfg=245
