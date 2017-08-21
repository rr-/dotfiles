"----------------------------------------
"- color scheme settings
"----------------------------------------

" Remove all existing highlighting and set the defaults.
colorscheme default

" Remove all highlighting
highlight clear Constant
highlight clear Number
highlight clear Statement
highlight clear PreProc
highlight clear Type
highlight clear Special
highlight clear Identifier

highlight String      term=underline cterm=NONE ctermfg=green
highlight Comment     term=bold      cterm=NONE ctermfg=cyan
highlight Error       term=reverse   cterm=NONE ctermbg=red
highlight LineNr      term=bold      cterm=NONE ctermfg=238
highlight NonText     term=bold      cterm=NONE ctermfg=yellow
highlight SpecialKey  term=NONE      cterm=NONE ctermfg=167
highlight StatusLine  term=bold      cterm=NONE ctermbg=234
highlight ColorColumn term=NONE      ctermbg=52
highlight SpellBad    term=NONE      ctermbg=52
highlight SpellCap    term=NONE      ctermbg=58
highlight SpellRare   term=NONE      ctermbg=23
highlight SpellLocal  term=NONE      ctermbg=23
highlight VertSplit   term=NONE      cterm=NONE ctermfg=245
