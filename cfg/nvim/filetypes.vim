"----------------------------------------
"- file-type specific settings
"----------------------------------------

"correct .lst filetype from assembler to text
au BufRead,BufNewFile *.lst set filetype=text

"screw buggy markdown syntax highlighting
au BufRead,BufNewFile *.md set filetype=text

"strip trailing whitespace for common source code
au FileType c,cc,cxx,cpp,h,hpp,java,php,python,ruby,vim
  \ au BufWritePre <buffer> :StripWhitespace

"enable spellcheck and hard wrapping for text files
au FileType text,markdown setlocal spell textwidth=79

"enable spellcheck and double gutter in git commit messages
au FileType gitcommit setlocal spell textwidth=72 colorcolumn=50,72

"enable spellcheck and double gutter in emails
au FileType mail setlocal spell textwidth=72 colorcolumn=72,80

"disable syntax for certain files
au FileType text,xml,json setlocal syntax=
autocmd BufNewFile,BufRead *.ts setlocal filetype=javascript

"automatically sort word lists and generate spell files
au BufWritePre */spell/*.add %sort i
au BufWritePost */spell/*.add silent mkspell! %

"disable spellcheck in urls
au FileType text,markdown syn match UrlNoSpell "\w\+:\/\/[^[:space:]]\+" contains=@NoSpell
