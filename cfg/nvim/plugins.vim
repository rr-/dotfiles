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

"config vim-move
let g:move_map_keys = 0
let g:move_key_modifier = 'C'           "c-j and c-k rather than default binding
let g:move_auto_indent = 0              "disable indentation aids
vmap <C-j> <Plug>MoveBlockDown
vmap <C-k> <Plug>MoveBlockUp
vmap <C-h> <Plug>MoveBlockLeft
vmap <C-l> <Plug>MoveBlockRight
nmap <C-j> <Plug>MoveLineDown
nmap <C-k> <Plug>MoveLineUp

"change tmux-navigator bindings
let g:tmux_navigator_no_mappings = 1
nnoremap <silent> <M-h> :TmuxNavigateLeft<CR>
nnoremap <silent> <M-j> :TmuxNavigateDown<CR>
nnoremap <silent> <M-k> :TmuxNavigateUp<CR>
nnoremap <silent> <M-l> :TmuxNavigateRight<CR>
nnoremap <silent> <M-\> :TmuxNavigatePrevious<CR>
tnoremap <silent> <M-h> <C-\><C-n>:TmuxNavigateLeft<CR>
tnoremap <silent> <M-j> <C-\><C-n>:TmuxNavigateDown<CR>
tnoremap <silent> <M-k> <C-\><C-n>:TmuxNavigateUp<CR>
tnoremap <silent> <M-l> <C-\><C-n>:TmuxNavigateRight<CR>
tnoremap <silent> <M-\> <C-\><C-n>:TmuxNavigatePrevious<CR>

"set black line length
let g:black_linelength = 79

"source code formatters
let g:vim_isort_map = ''
nnoremap <silent> <C-i> :Isort<CR>
nnoremap <silent> <C-b> :Black<CR>
