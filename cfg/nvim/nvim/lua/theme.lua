-- ----------------------------------------
-- color scheme settings
-- ----------------------------------------

vim.cmd('colorscheme vim')
vim.o.termguicolors = false
vim.o.background = 'light'

vim.api.nvim_set_hl(0, 'Number',       { ctermfg = 217 })
vim.api.nvim_set_hl(0, 'PreProc',      { ctermfg = 4 })
vim.api.nvim_set_hl(0, 'Special',      { })
vim.api.nvim_set_hl(0, 'Constant',     { ctermfg = 174 })
vim.api.nvim_set_hl(0, 'String',       { ctermfg = 'green' })
vim.api.nvim_set_hl(0, 'Identifier',   { ctermfg = 74 })
vim.api.nvim_set_hl(0, 'Statement',    { ctermfg = 167 })
vim.api.nvim_set_hl(0, 'Type',         { ctermfg = 146 })
vim.api.nvim_set_hl(0, 'Comment',      { ctermfg = 110})
vim.api.nvim_set_hl(0, 'Error',        { ctermbg = 196, ctermfg = 16 })
vim.api.nvim_set_hl(0, 'Todo',         { ctermbg = 58 })
vim.api.nvim_set_hl(0, 'NonText',      { bold = true, ctermfg = 'yellow' })
vim.api.nvim_set_hl(0, 'SpecialKey',   { ctermfg = 167 })
vim.api.nvim_set_hl(0, 'LineNr',       { ctermfg = 238 })
vim.api.nvim_set_hl(0, 'ErrorMsg',     { ctermbg = 196, ctermfg = 16 })
vim.api.nvim_set_hl(0, 'StatusLine',   { ctermbg = 235 })
vim.api.nvim_set_hl(0, 'StatusLineNC', { ctermbg = 235 })
vim.api.nvim_set_hl(0, 'Folded',       { ctermfg = 242, ctermbg = 233 })
vim.api.nvim_set_hl(0, 'ColorColumn',  { ctermbg = 52 })
vim.api.nvim_set_hl(0, 'SignColumn',   { ctermbg = 58 })
vim.api.nvim_set_hl(0, 'SpellBad',     { ctermbg = 52 })
vim.api.nvim_set_hl(0, 'SpellCap',     { ctermbg = 58 })
vim.api.nvim_set_hl(0, 'SpellRare',    { ctermbg = 23 })
vim.api.nvim_set_hl(0, 'SpellLocal',   { ctermbg = 23 })
vim.api.nvim_set_hl(0, 'Search',       { ctermbg = 142, ctermfg = 255 })
vim.api.nvim_set_hl(0, 'CursorLine',   { })
vim.api.nvim_set_hl(0, 'CursorLineNr', { ctermfg = 173 })
vim.api.nvim_set_hl(0, 'VertSplit',    { ctermfg = 235, ctermbg = 235 })
vim.api.nvim_set_hl(0, 'EndOfBuffer',  { ctermfg = 232 })
vim.api.nvim_set_hl(0, 'TabLineFill',  { ctermbg = 234 })
vim.api.nvim_set_hl(0, 'TabLine',      { ctermfg = 250, ctermbg = 238 })
vim.api.nvim_set_hl(0, 'TabLineSel',   { ctermfg = 255, ctermbg = 232 })

vim.api.nvim_set_hl(0, 'ZenBg',        { ctermbg = 233 })
vim.api.nvim_set_hl(0, 'Pmenu',        { link = 'Normal' })

vim.o.cursorline = true
vim.o.statusline = '%f %m%r%=Col:%c Line:%l/%L'

vim.api.nvim_set_hl(0, 'pythonFunction', {bold, ctermfg = 111, ctermbg = 233 })
