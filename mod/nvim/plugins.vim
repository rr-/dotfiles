"----------------------------------------
"- plugin options
"----------------------------------------

"fzf
if has('nvim')
  let g:fzf_nvim_statusline = 0
  function! s:fzf_statusline()
    "don't set any colors explicitly
    setlocal statusline=%#fzf1#\ >\ %#fzf2#fz%#fzf3#f
  endfunction
  autocmd! User FzfStatusLine call <SID>fzf_statusline()
endif

"localvimrc
let g:localvimrc_persistent = 1         "remember decisions to load given lvimrc

"config vim-move
let g:move_key_modifier = 'C'           "c-j and c-k rather than default binding
let g:move_auto_indent = 0              "disable indentation aids

"gitgutter
let g:gitgutter_sign_column_always = 1  "don't 'jump' between buffers
set updatetime=250                      "be more responsive
