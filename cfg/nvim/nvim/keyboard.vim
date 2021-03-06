"----------------------------------------
"- keyboard bindings
"----------------------------------------

"set the leader key to -
let mapleader = "-"
"prevent vinegar from binding to -
nnoremap - -

"movement over visual lines, not physical lines
map <buffer> <silent> k gk
map <buffer> <silent> j gj
"ctrl+s = save
inoremap <silent> <C-s> <Esc>:update<CR>
nnoremap <silent> <C-s> :<C-u>update<CR>
"ctrl+c = copy
inoremap <silent> <C-c> <Esc>"+y
nnoremap <silent> <C-c> "+y
"ctrl+z = open shell
if has('nvim')
  nnoremap <silent> <C-z> :te<CR>
else
  nnoremap <silent> <C-z> :sh<CR>
endif
"ctrl+q = close window
inoremap <silent> <C-q> <Esc>:q<CR>
nnoremap <silent> <C-q> :q<CR>
"ctrl+w ctrl+m = open new file vertically
nnoremap <silent> <C-w><C-m> :vne<CR>
nnoremap <silent> <C-w>m :vne<CR>
"save with sudo
cnoremap w!! w !sudo tee >/dev/null %
"disable stupid manual pages
nnoremap <silent> <S-K> <nop>
vnoremap <silent> <S-K> <nop>
"easier formatting of paragraphs
vnoremap Q gq
nnoremap Q gqap
"fuzzy file finder
nnoremap <C-e> :Rg<CR>
nnoremap <C-p> :Files<CR>
nnoremap <C-l> :Buffers<CR>
"convenient new tab
nnoremap gn :tabnew<CR>
"go to line
nnoremap <expr> <silent> <CR> v:count ? ":<C-U><Esc>" . v:count . "G" : "<CR>"

"toggle .h .cpp
function! SwitchSourceHeader()
  let ext = expand("%:e")
  if (ext == "cpp" || ext == "c" || ext == "cc")
    silent! find %:t:r.h | edit %:r.h
  else
    silent! find %:t:r.cc | silent! find %:t:r.c | silent! find %:t:r.cpp
  endif
endfunction
nnoremap <F4> :call SwitchSourceHeader()<CR>

"exit terminal mode via escape
tnoremap <Esc> <C-\><C-n>

"file explorer
  imap <F3> <Esc><Plug>VinegarUp
  nmap <F3> <Plug>VinegarUp
"EasyAlign
  "normal mode (e.g. gaip)
  nmap ga <Plug>(EasyAlign)
  "visual mode (e.g. vipga)
  xmap ga <Plug>(EasyAlign)

"readline emulation
"(rsi.vim breaks a lot of things and caused me big frustration)
cnoremap <C-a> <Home>
cnoremap <C-e> <End>
cnoremap <C-b> <Left>
cnoremap <C-f> <Right>
cnoremap <C-p> <Up>
cnoremap <C-n> <Down>
cnoremap <C-d> <Del>
cnoremap <C-k> <C-\>e getcmdpos() == 1 ? '' : getcmdline()[:getcmdpos()-2]<CR>
cnoremap <M-b> <S-Left>
cnoremap <M-f> <S-Right>

if has("digraphs")
  digraph .. 8230 " …
  digraph xx 215 " ×
endif

"highlight search inplace
map <Leader>* :let @/ = '\<'.expand('<cword>').'\>'\|set hlsearch<C-M>
map <Leader>g* :let @/ = expand('<cword>')\|set hlsearch<C-M>

inoreabbr <expr> ts# strftime("%Y-%m-%d")
