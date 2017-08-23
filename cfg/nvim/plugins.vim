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
set signcolumn=yes                      "don't 'jump' between buffers
set updatetime=250                      "be more responsive

"change tmux-navigator bindings
let g:tmux_navigator_no_mappings = 1
nnoremap <silent> <M-h> :TmuxNavigateLeft<cr>
nnoremap <silent> <M-j> :TmuxNavigateDown<cr>
nnoremap <silent> <M-k> :TmuxNavigateUp<cr>
nnoremap <silent> <M-l> :TmuxNavigateRight<cr>
nnoremap <silent> <M-\> :TmuxNavigatePrevious<cr>
inoremap <silent> <M-h> <esc>:TmuxNavigateLeft<cr>
inoremap <silent> <M-j> <esc>:TmuxNavigateDown<cr>
inoremap <silent> <M-k> <esc>:TmuxNavigateUp<cr>
inoremap <silent> <M-l> <esc>:TmuxNavigateRight<cr>
inoremap <silent> <M-\> <esc>:TmuxNavigatePrevious<cr>
