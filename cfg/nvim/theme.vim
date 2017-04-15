"----------------------------------------
"- color scheme settings
"----------------------------------------

"basic vim
if has('nvim')
  set termguicolors
  let theme='PaperColor'
else
  let theme='hemisu'
endif
let &background='light'
silent! execute 'colorscheme '.theme

"fix ColorColumn on dark backgrounds
if &background == 'dark'
  highlight ColorColumn ctermbg=235
else
  highlight ColorColumn ctermbg=255
end
highlight Normal guibg=NONE

"airline color scheme
if &background == 'dark'
  let g:airline_theme = 'ubaryd'
else
  let g:airline_theme = 'sol'
endif
"allow use of special characters that are supplied by terminal font
let g:airline_powerline_fonts = 1
