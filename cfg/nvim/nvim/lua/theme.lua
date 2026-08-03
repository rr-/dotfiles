-- ----------------------------------------
-- color scheme settings
-- ----------------------------------------

-- Colors come in by role from ~/.config/theme.d/<theme>.colors.lua, which
-- theme(1) renders out of cfg/theme/roles.toml against the palettes in
-- cfg/wezterm/colors. Spelling them out as gui colors means this doesn't
-- depend on the terminal honoring our 256-color remap, so it survives ssh from
-- a terminal that only does truecolor; taking them by role means the tone
-- behind the statusline here is the same one behind the tmux status bar.

local THEME_FILE = vim.fn.expand('~/.config/theme')
local COLORS_DIR = vim.fn.expand('~/.config/theme.d')

-- $THEME describes the terminal we're displayed on, which is what actually
-- matters and which .zshrc already resolved; the file theme(1) writes
-- only describes this machine, so it loses when we're an ssh session from a
-- differently themed client. Fall back to whatever the terminal reported over
-- OSC 11, then to that file, then to light - the 'background' default is dark,
-- so an unset option tells us nothing.
local function detect_background()
  local env = vim.env.THEME
  if env == 'dark' or env == 'light' then
    return env
  end
  if vim.api.nvim_get_option_info2('background', {}).was_set then
    return vim.o.background
  end
  local ok, lines = pcall(vim.fn.readfile, THEME_FILE)
  if ok and lines[1] then
    local theme = vim.trim(lines[1])
    if theme == 'dark' or theme == 'light' then
      return theme
    end
  end
  return 'light'
end

-- the generated table for one theme, or an empty one if it isn't there yet
local function load_colors(theme)
  local path = COLORS_DIR .. '/' .. theme .. '.colors.lua'
  local chunk = loadfile(path)
  if not chunk then
    vim.notify('no colors for ' .. theme .. ' - run theme', vim.log.levels.WARN)
    return setmetatable({}, { __index = function() return nil end })
  end
  return chunk()
end

local function apply_highlights()
  local p = load_colors(vim.o.background)
  local hl = vim.api.nvim_set_hl

  hl(0, 'Number',                { fg = p.syntax_number_alt, ctermfg = 217 })
  hl(0, 'PreProc',               { fg = p.syntax_preproc, ctermfg = 4 })
  hl(0, 'Special',               { })
  hl(0, 'Constant',              { fg = p.syntax_constant_alt, ctermfg = 174 })
  hl(0, 'String',                { ctermfg = 'green' })
  hl(0, 'Identifier',            { fg = p.syntax_identifier, ctermfg = 252 })
  hl(0, 'Statement',             { fg = p.syntax_special_key, ctermfg = 167 })
  hl(0, 'Type',                  { fg = p.syntax_type, ctermfg = 146 })
  hl(0, 'Comment',               { fg = p.syntax_comment, ctermfg = 107 })
  hl(0, 'Error',                 { bg = p.syntax_error_bg, fg = p.syntax_error_fg, ctermbg = 196, ctermfg = 16 })
  hl(0, 'Todo',                  { bg = p.state_attention_bg, ctermbg = 58 })
  hl(0, 'NonText',               { ctermfg = 'yellow', bold = true })
  hl(0, 'SpecialKey',            { fg = p.syntax_special_key, ctermfg = 167 })
  hl(0, 'LineNr',                { fg = p.surface_overlay, ctermfg = 238 })
  hl(0, 'ErrorMsg',              { bg = p.syntax_error_bg, fg = p.syntax_error_fg, ctermbg = 196, ctermfg = 16 })
  hl(0, 'StatusLine',            { bg = p.surface_raised, ctermbg = 235 })
  hl(0, 'StatusLineNC',          { bg = p.surface_raised, ctermbg = 235 })
  hl(0, 'Folded',                { bg = p.editor_folded_bg, fg = p.text_faint, ctermfg = 242, ctermbg = 233 })
  hl(0, 'ColorColumn',           { bg = p.state_error_bg, ctermbg = 52 })
  hl(0, 'SignColumn',            { bg = p.state_attention_bg, ctermbg = 58 })
  hl(0, 'SpellBad',              { bg = p.state_error_bg, ctermbg = 52 })
  hl(0, 'SpellCap',              { bg = p.state_attention_bg, ctermbg = 58 })
  hl(0, 'SpellRare',             { bg = p.state_info_bg, ctermbg = 23 })
  hl(0, 'SpellLocal',            { bg = p.state_info_bg, ctermbg = 23 })
  hl(0, 'Search',                { bg = p.editor_search_bg, fg = p.text_strong, ctermbg = 142, ctermfg = 255 })
  hl(0, 'Cursor',                { bg = p.editor_cursor_bg, fg = p.editor_cursor_fg })
  hl(0, 'CursorLine',            { bg = p.editor_cursorline })
  hl(0, 'CursorLineNr',          { fg = p.state_warning, ctermfg = 173 })
  hl(0, 'VertSplit',             { fg = p.surface_raised, bg = p.surface_raised, ctermfg = 235, ctermbg = 235 })
  hl(0, 'EndOfBuffer',           { fg = p.surface_sunken, ctermfg = 232 })
  hl(0, 'TabLineFill',           { fg = p.surface_base, ctermbg = 234 })
  hl(0, 'TabLine',               { fg = p.text_dim, bg = p.surface_overlay, ctermfg = 250, ctermbg = 238 })
  hl(0, 'TabLineSel',            { fg = p.text_strong, bg = p.surface_sunken, ctermfg = 255, ctermbg = 232 })

  hl(0, 'pythonFunction',        { fg = p.editor_function_fg, bg = p.editor_folded_bg, ctermfg = 111, ctermbg = 233 })
  hl(0, 'FzfLuaCursorLine',      { bg = p.editor_search_bg, ctermbg = 142 })
  hl(0, 'FzfLuaCursorLineNr',    { })

  hl(0, '@identifier',           { fg = p.text_strong, ctermfg = 255 })
  hl(0, '@comment',              { fg = p.syntax_comment, ctermfg = 107 })
  hl(0, '@comment.todo',         { bg = p.state_attention_bg, ctermbg = 58 })
  hl(0, '@type',                 { fg = p.syntax_type_alt, ctermfg = 138 })
  hl(0, '@type.builtin',         { link = '@type' })
  hl(0, '@keyword',              { fg = p.syntax_keyword, ctermfg = 203 })
  hl(0, '@keyword.type',         { link = '@keyword' })
  hl(0, '@keyword.repeat',       { link = '@keyword' })
  hl(0, '@keyword.conditional',  { link = '@keyword' })
  hl(0, '@null',                 { link = '@keyword' })
  hl(0, '@label',                { fg = p.syntax_keyword, ctermfg = 203 })
  hl(0, '@operator',             { })
  hl(0, '@constant',             { fg = p.syntax_constant, ctermfg = 75 })
  hl(0, '@string',               { fg = p.syntax_string, bg = p.syntax_string_bg, ctermfg = 156, bold = true })
  hl(0, '@string.documentation', { fg = p.text_faint, ctermfg = 242 })
  hl(0, '@character',            { link = '@string' })
  hl(0, '@number',               { fg = p.syntax_number, ctermfg = 217 })
  hl(0, '@number.float',         { link = '@number' })
  hl(0, '@boolean',              { link = '@number' })
  hl(0, '@function',             { fg = p.syntax_function, ctermfg = 15, bold = true })
  hl(0, '@struct.specifier',     { link = '@keyword' })

  hl(0, 'Pmenu',                 { link = 'Normal' })
end

vim.o.termguicolors = true
vim.o.background = detect_background()

vim.cmd('colorscheme vim')
apply_highlights()

-- Re-apply when the theme changes underneath us: theme(1) sets
-- 'background' over the rpc socket, and the TUI sets it when the terminal
-- reports a new background color. Changing 'background' reloads the color
-- scheme, which wipes our highlights, so hook the reload rather than
-- OptionSet - the latter fires before it.
vim.api.nvim_create_autocmd('ColorScheme', { callback = apply_highlights })

vim.o.cursorline = true
vim.o.statusline = '%f %m%r%=Col:%c Line:%l/%L'
vim.g.c_no_curly_error = 1  -- breaks in the simplest __VA_ARGS__ macros

-- LUA support broken as of 2025-12-30
-- require 'nvim-treesitter.config'.setup {
--   -- A list of parser names, or "all" (the listed parsers MUST always be installed)
--   ensure_installed = { "c", "lua", "vim", "vimdoc", "query", "markdown", "markdown_inline" },
--
--   -- Install parsers synchronously (only applied to `ensure_installed`)
--   sync_install = false,
--
--   -- Automatically install missing parsers when entering buffer
--   -- Recommendation: set to false if you don't have `tree-sitter` CLI installed locally
--   auto_install = true,
--
--   -- List of parsers to ignore installing (or "all")
--   ignore_install = { "javascript" },
--
--   ---- If you need to change the installation directory of the parsers (see -> Advanced Setup)
--   -- parser_install_dir = "/some/path/to/store/parsers", -- Remember to run vim.opt.runtimepath:append("/some/path/to/store/parsers")!
--
--   highlight = {
--     enable = true,
--
--     -- NOTE: these are the names of the parsers and not the filetype. (for example if you want to
--     -- disable highlighting for the `tex` filetype, you need to include `latex` in this list as this is
--     -- the name of the parser)
--     -- list of language that will be disabled
--     disable = { "c", "rust" },
--     -- Or use a function for more flexibility, e.g. to disable slow treesitter highlight for large files
--     disable = function(lang, buf)
--         local max_filesize = 100 * 1024 -- 100 KB
--         local ok, stats = pcall(vim.loop.fs_stat, vim.api.nvim_buf_get_name(buf))
--         if ok and stats and stats.size > max_filesize then
--             return true
--         end
--     end,
--
--     -- Setting this to true will run `:h syntax` and tree-sitter at the same time.
--     -- Set this to `true` if you depend on 'syntax' being enabled (like for indentation).
--     -- Using this option may slow down your editor, and you may see some duplicate highlights.
--     -- Instead of true it can also be a list of languages
--     additional_vim_regex_highlighting = false,
--   },
-- }
