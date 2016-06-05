"----------------------------------------
"- color scheme settings
"----------------------------------------

"basic vim
if $LIGHTNESS ==? 'light'     "$LIGHTNESS exported by zshrc
  set background=light
  silent! colorscheme hemisu
else
  set background=dark
  silent! colorscheme sorcerer
endif

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
