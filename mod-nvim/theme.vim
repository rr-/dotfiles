"----------------------------------------
"- color scheme settings
"----------------------------------------

"basic vim
if has('nvim')
  set termguicolors
  if $LIGHTNESS ==? 'light'     "$LIGHTNESS exported by zshrc
    let theme='PaperColor'
  else
    let theme='Tomorrow-Night'
  endif
else
  if $LIGHTNESS ==? 'light'     "$LIGHTNESS exported by zshrc
    let theme='hemisu'
  else
    let theme='sorcerer'
  endif
endif
let &background=$LIGHTNESS
silent! execute 'colorscheme '.theme

"fix ColorColumn on dark backgrounds
if &background == 'dark'
  highlight ColorColumn ctermbg=235
else
  highlight Normal ctermbg=NONE
  highlight ColorColumn ctermbg=255
end

"airline color scheme
if &background == 'dark'
  let g:airline_theme = 'ubaryd'
else
  let g:airline_theme = 'sol'
endif
"allow use of special characters that are supplied by terminal font
let g:airline_powerline_fonts = 1
