-- ----------------------------------------
-- file-type specific settings
-- ----------------------------------------

-- correct .lst filetype from assembler to text
vim.api.nvim_create_autocmd({'BufRead', 'BufNewFile'}, {
  pattern = '*.lst',
  command = 'set filetype=text'
})

-- correct .def filetype from assembler to c
vim.api.nvim_create_autocmd({'BufRead', 'BufNewFile'}, {
  pattern = '*.def',
  command = 'set syntax=c'
})

-- strip trailing whitespace for common source code
vim.api.nvim_create_autocmd('FileType', {
  pattern = 'c,cc,cxx,cpp,h,hpp,java,php,python,ruby,vim',
  callback = function()
    vim.api.nvim_create_autocmd('BufWritePre', {
      buffer = 0,
      command = 'StripWhitespace'
    })
  end
})

-- set c/c++ options
vim.api.nvim_create_autocmd('FileType', {
  pattern = 'c,cc,cxx,cpp,h,hpp',
  callback = function()
    vim.bo.commentstring = '// %s'
  end
})

-- enable spellcheck and hard wrapping for text files
vim.api.nvim_create_autocmd('FileType', {
  pattern = 'text,markdown',
  command = 'setlocal spell textwidth=79'
})

-- enable spellcheck and double gutter in git commit messages
vim.api.nvim_create_autocmd('FileType', {
  pattern = 'gitcommit',
  command = 'setlocal spell textwidth=72 colorcolumn=50,72'
})

-- enable spellcheck and double gutter in emails
vim.api.nvim_create_autocmd('FileType', {
  pattern = 'mail',
  command = 'setlocal spell textwidth=72 colorcolumn=72,80'
})

-- disable syntax for certain files
vim.api.nvim_create_autocmd('FileType', {
  pattern = 'text,xml,json',
  command = 'setlocal syntax='
})

vim.api.nvim_create_autocmd({'BufNewFile', 'BufRead'}, {
  pattern = '*.ts',
  command = 'setlocal filetype=javascript'
})

-- automatically sort word lists and generate spell files
vim.api.nvim_create_autocmd('BufWritePre', {
  pattern = '*/spell/*.add',
  command = '%sort i'
})

vim.api.nvim_create_autocmd('BufWritePost', {
  pattern = '*/spell/*.add',
  command = 'silent mkspell! %'
})

-- disable spellcheck in urls
vim.api.nvim_create_autocmd('FileType', {
  pattern = 'text,markdown',
  command = 'syn match UrlNoSpell "\\w\\+:\\/\\/[^[:space:]]\\+" contains=@NoSpell'
})

-- don't skip over keywords
vim.api.nvim_create_autocmd('FileType', {
  pattern = '*',
  command = 'setlocal iskeyword=@,48-57,_,192-255'
})
