"----------------------------------------
"- keyboard bindings
"----------------------------------------

"set the leader key to -
let mapleader = "-"
"movement over visual lines, not physical lines
map <buffer> <silent> k gk
map <buffer> <silent> j gj
"ctrl+s = save
inoremap <silent> <C-s> <Esc>:update<CR>
nnoremap <silent> <C-s> :<C-u>update<CR>
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
"make motion search easier to access
nmap <leader>z <Plug>(easymotion-s)
"save with sudo
cnoremap w!! w !sudo tee >/dev/null %
"disable stupid manual pages
nnoremap <silent> <S-K> <nop>
vnoremap <silent> <S-K> <nop>
"easier formatting of paragraphs
vnoremap Q gq
nnoremap Q gqap
"fuzzy file finder
nnoremap <C-e> :Ag<CR>
nnoremap <C-p> :Files<CR>
nnoremap <C-m> :Buffers<CR>
"toggle .h .cpp
nnoremap <F4> :e %:p:s,.h$,.X123X,:s,.cc$,.h,:s,.X123X$,.cc,<CR>
"NERDTree
  "toggle NERDtree
  inoremap <F2> <esc>:NERDTreeToggle<CR>
  nnoremap <F2> :NERDTreeToggle<CR>
  "locate current file in NERDtree
  inoremap <F3> <esc>:NERDTreeFind<CR>
  nnoremap <F3> :NERDTreeFind<CR>
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
