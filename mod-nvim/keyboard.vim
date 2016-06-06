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
nnoremap <C-p> :Files<CR>
nnoremap <C-m> :Buffers<CR>
"toggle NERDtree
"au VimEnter * inoremap <F2> <esc>:NERDTreeToggle<CR>
"au VimEnter * nnoremap <F2> :NERDTreeToggle<CR>
inoremap <F2> <esc>:NERDTreeToggle<CR>
nnoremap <F2> :NERDTreeToggle<CR>
"locate current file in NERDtree
inoremap <F3> <esc>:NERDTreeFind<CR>
nnoremap <F3> :NERDTreeFind<CR>
"EasyAlign
nnoremap ga <Plug>(EasyAlign) "normal mode (e.g. gaip)
xnoremap ga <Plug>(EasyAlign) "visual mode (e.g. vipga)
