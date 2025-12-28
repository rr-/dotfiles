-- ----------------------------------------
-- color scheme settings
-- ----------------------------------------

vim.cmd('colorscheme vim')

vim.o.termguicolors = true
vim.o.background = 'light'

vim.api.nvim_set_hl(0, 'Number',                { fg = '#ff0000', ctermfg = 217 })
vim.api.nvim_set_hl(0, 'PreProc',               { fg = "#005FAF", ctermfg = 4 })
vim.api.nvim_set_hl(0, 'Special',               { })
vim.api.nvim_set_hl(0, 'Constant',              { fg = "#AF5F5F", ctermfg = 174 })
vim.api.nvim_set_hl(0, 'String',                { ctermfg = 'green' })
vim.api.nvim_set_hl(0, 'Identifier',            { fg = "#212121", ctermfg = 252 })
vim.api.nvim_set_hl(0, 'Statement',             { fg = "#D75F5F", ctermfg = 167 })
vim.api.nvim_set_hl(0, 'Type',                  { fg = "#5F5F87", ctermfg = 146 })
vim.api.nvim_set_hl(0, 'Comment',               { fg = "#5F87AF", ctermfg = 110})
vim.api.nvim_set_hl(0, 'Error',                 { bg = "#FF0000", fg = "#ffffff", ctermbg = 196, ctermfg = 16 })
vim.api.nvim_set_hl(0, 'Todo',                  { bg = "#FFFFD7", ctermbg = 58 })
vim.api.nvim_set_hl(0, 'NonText',               { ctermfg = 'yellow', bold = true })
vim.api.nvim_set_hl(0, 'SpecialKey',            { fg = "#D75F5F", ctermfg = 167 })
vim.api.nvim_set_hl(0, 'LineNr',                { fg = "#BBBBBB", ctermfg = 238 })
vim.api.nvim_set_hl(0, 'ErrorMsg',              { bg = "#FF0000", fg = "#ffffff", ctermbg = 196, ctermfg = 16 })
vim.api.nvim_set_hl(0, 'StatusLine',            { bg = "#DCDCDC", ctermbg = 235 })
vim.api.nvim_set_hl(0, 'StatusLineNC',          { bg = "#DCDCDC", ctermbg = 235 })
vim.api.nvim_set_hl(0, 'Folded',                { bg = "#F2F2F2", fg = "#8F8F8F", ctermfg = 242, ctermbg = 233 })
vim.api.nvim_set_hl(0, 'ColorColumn',           { bg = "#FFD7D7", ctermbg = 52 })
vim.api.nvim_set_hl(0, 'SignColumn',            { bg = "#FFFFD7", ctermbg = 58 })
vim.api.nvim_set_hl(0, 'SpellBad',              { bg = "#FFD7D7", ctermbg = 52 })
vim.api.nvim_set_hl(0, 'SpellCap',              { bg = "#FFFFD7", ctermbg = 58 })
vim.api.nvim_set_hl(0, 'SpellRare',             { bg = "#D7FFFF", ctermbg = 23 })
vim.api.nvim_set_hl(0, 'SpellLocal',            { bg = "#D7FFFF", ctermbg = 23 })
vim.api.nvim_set_hl(0, 'Search',                { bg = "#FFFF87", fg = "#000000", ctermbg = 142, ctermfg = 255 })
vim.api.nvim_set_hl(0, 'Cursor',                { bg = "#40AF40", fg = "#FFFFFF" })
vim.api.nvim_set_hl(0, 'CursorLine',            { bg = "#F4F8EA" })
vim.api.nvim_set_hl(0, 'CursorLineNr',          { fg = "#D7875F", ctermfg = 173 })
vim.api.nvim_set_hl(0, 'VertSplit',             { fg = "#DCDCDC", bg = "#DCDCDC", ctermfg = 235, ctermbg = 235 })
vim.api.nvim_set_hl(0, 'EndOfBuffer',           { fg = "#FDFDFD", ctermfg = 232 })
vim.api.nvim_set_hl(0, 'TabLineFill',           { fg = "#E7E7E7", ctermbg = 234 })
vim.api.nvim_set_hl(0, 'TabLine',               { fg = "#373737", bg = "#BBBBBB", ctermfg = 250, ctermbg = 238 })
vim.api.nvim_set_hl(0, 'TabLineSel',            { fg = "#000000", bg = "#FDFDFD", ctermfg = 255, ctermbg = 232 })

vim.api.nvim_set_hl(0, 'pythonFunction',        { fg = "#005FAF", bg = "#F2F2F2", ctermfg = 111, ctermbg = 233 })
vim.api.nvim_set_hl(0, 'FzfLuaCursorLine',      { bg = "#FFFF87", ctermbg = 142 })
vim.api.nvim_set_hl(0, 'FzfLuaCursorLineNr',    { })

vim.api.nvim_set_hl(0, '@identifier',           { fg = "#000000", ctermfg = 255 })
vim.api.nvim_set_hl(0, '@comment',              { fg = "#8F8F8F", ctermfg = 242 })
vim.api.nvim_set_hl(0, '@comment.todo',         { bg = "#FFFFD7", ctermbg = 58 })
vim.api.nvim_set_hl(0, '@type',                 { fg = "#408000", ctermfg = 138 })
vim.api.nvim_set_hl(0, '@type.builtin',         { link = '@type' })
vim.api.nvim_set_hl(0, '@keyword',              { fg = "#D70000", ctermfg = 203 })
vim.api.nvim_set_hl(0, '@keyword.type',         { link = '@keyword' })
vim.api.nvim_set_hl(0, '@keyword.repeat',       { link = '@keyword' })
vim.api.nvim_set_hl(0, '@keyword.conditional',  { link = '@keyword' })
vim.api.nvim_set_hl(0, '@null',                 { link = '@keyword' })
vim.api.nvim_set_hl(0, '@label',                { fg = "#D70000", ctermfg = 203 })
vim.api.nvim_set_hl(0, '@operator',             { })
vim.api.nvim_set_hl(0, '@constant',             { fg = "#0087D7", ctermfg = 75 })
vim.api.nvim_set_hl(0, '@string',               { fg = "#5FAF00", bg = "#F8FFF0", ctermfg = 156, bold = true })
vim.api.nvim_set_hl(0, '@string.documentation', { fg = "#8F8F8F", ctermfg = 242 })
vim.api.nvim_set_hl(0, '@character',            { link = '@string' })
vim.api.nvim_set_hl(0, '@number',               { fg = "#D78000", ctermfg = 217 })
vim.api.nvim_set_hl(0, '@number.float',         { link = '@number' })
vim.api.nvim_set_hl(0, '@boolean',              { link = '@number' })
vim.api.nvim_set_hl(0, '@function',             { fg = "#414141", ctermfg = 15, bold = true })
vim.api.nvim_set_hl(0, '@struct.specifier',     { link = '@keyword' })

vim.api.nvim_set_hl(0, 'Pmenu',                 { link = 'Normal' })

vim.o.cursorline = true
vim.o.statusline = '%f %m%r%=Col:%c Line:%l/%L'

require 'nvim-treesitter.config'.setup {
  -- A list of parser names, or "all" (the listed parsers MUST always be installed)
  ensure_installed = { "c", "lua", "vim", "vimdoc", "query", "markdown", "markdown_inline" },

  -- Install parsers synchronously (only applied to `ensure_installed`)
  sync_install = false,

  -- Automatically install missing parsers when entering buffer
  -- Recommendation: set to false if you don't have `tree-sitter` CLI installed locally
  auto_install = true,

  -- List of parsers to ignore installing (or "all")
  ignore_install = { "javascript" },

  ---- If you need to change the installation directory of the parsers (see -> Advanced Setup)
  -- parser_install_dir = "/some/path/to/store/parsers", -- Remember to run vim.opt.runtimepath:append("/some/path/to/store/parsers")!

  highlight = {
    enable = true,

    -- NOTE: these are the names of the parsers and not the filetype. (for example if you want to
    -- disable highlighting for the `tex` filetype, you need to include `latex` in this list as this is
    -- the name of the parser)
    -- list of language that will be disabled
    disable = { "c", "rust" },
    -- Or use a function for more flexibility, e.g. to disable slow treesitter highlight for large files
    disable = function(lang, buf)
        local max_filesize = 100 * 1024 -- 100 KB
        local ok, stats = pcall(vim.loop.fs_stat, vim.api.nvim_buf_get_name(buf))
        if ok and stats and stats.size > max_filesize then
            return true
        end
    end,

    -- Setting this to true will run `:h syntax` and tree-sitter at the same time.
    -- Set this to `true` if you depend on 'syntax' being enabled (like for indentation).
    -- Using this option may slow down your editor, and you may see some duplicate highlights.
    -- Instead of true it can also be a list of languages
    additional_vim_regex_highlighting = false,
  },
}
