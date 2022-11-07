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

highlight Constant     term=NONE      cterm=NONE ctermfg=174
highlight String       term=NONE      cterm=NONE ctermfg=green
highlight Identifier   term=NONE      cterm=NONE ctermfg=74
highlight Statement    term=NONE      cterm=NONE ctermfg=167
highlight Type         term=NONE      cterm=NONE ctermfg=146
highlight Comment      term=NONE      cterm=NONE ctermfg=110
highlight Error        term=NONE      cterm=NONE ctermbg=196 ctermfg=16
highlight Todo         term=NONE      ctermbg=58 ctermfg=NONE
highlight NonText      term=bold      cterm=NONE ctermfg=yellow
highlight SpecialKey   term=NONE      cterm=NONE ctermfg=167
highlight LineNr       term=NONE      cterm=NONE ctermfg=238
highlight ErrorMsg     term=NONE      cterm=NONE ctermbg=196 ctermfg=16
highlight StatusLine   term=NONE      cterm=NONE ctermbg=235
highlight StatusLineNC term=NONE      cterm=NONE ctermbg=235
highlight Folded       term=NONE      ctermfg=242 ctermbg=233
highlight ColorColumn  term=NONE      ctermbg=52
highlight SignColumn   term=NONE      ctermbg=58
highlight SpellBad     term=NONE      ctermbg=52
highlight SpellCap     term=NONE      ctermbg=58
highlight SpellRare    term=NONE      ctermbg=23
highlight SpellLocal   term=NONE      ctermbg=23
highlight Search       term=NONE      ctermbg=142 ctermfg=255
highlight CursorLine   term=NONE      cterm=NONE ctermfg=NONE ctermbg=NONE
highlight CursorLineNr term=NONE      cterm=NONE ctermfg=173
highlight VertSplit    term=NONE      cterm=NONE ctermfg=235 ctermbg=235
" later replace this with fillchars
highlight EndOfBuffer  term=NONE      cterm=NONE ctermfg=232
highlight TabLineFill  term=NONE      cterm=NONE ctermbg=234
highlight TabLine      term=NONE      cterm=NONE ctermfg=250 ctermbg=238
highlight TabLineSel   term=NONE      cterm=NONE ctermfg=255 ctermbg=232

highlight! link Pmenu Normal

set cursorline
set statusline=%f\ %m%r%=Col:%c\ Line:%l/%L

highlight pythonFunction term=NONE cterm=BOLD ctermfg=111 ctermbg=233
