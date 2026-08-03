-- Colors by role from ~/.config/theme.d/<theme>.colors.lua, rendered by
-- theme(1) - see cfg/theme/roles.toml.

local THEME_FILE = vim.fn.expand('~/.config/theme')
local COLORS_DIR = vim.fn.expand('~/.config/theme.d')

-- fzf-lua overrides only the match colors, so the picker otherwise keeps
-- whatever $FZF_DEFAULT_OPTS this neovim inherited. Put ours back on every
-- repaint.
local FZF_BASE_OPTS = (vim.env.FZF_DEFAULT_OPTS or ''):gsub('%-%-color[=%s]%S+', '')

-- $THEME first: it describes the terminal we're on, and loses to nothing.
-- 'background' is last because its default is dark, so only was_set means
-- the terminal actually answered. Second return: did we find a real answer.
local function detect_background()
  local env = vim.env.THEME
  if env == 'dark' or env == 'light' then
    return env, true
  end
  local ok, lines = pcall(vim.fn.readfile, THEME_FILE)
  if ok and lines[1] then
    local theme = vim.trim(lines[1])
    if theme == 'dark' or theme == 'light' then
      return theme, true
    end
  end
  if vim.api.nvim_get_option_info2('background', {}).was_set then
    return vim.o.background, false
  end
  return 'light', false
end

-- Neovim keeps a TermResponse handler that rewrites 'background' from any OSC
-- 11 answer, for life - it only drops it for a 'background' set from
-- vimscript, and this is lua. tmux passes the query on only while the pane is
-- in front of a client, so the answer can land when you switch back to the
-- window, hours later, and repaint a running editor. Drop the handler.
local function ignore_terminal_background()
  local ok, autocmds = pcall(vim.api.nvim_get_autocmds, {
    group = 'nvim.tty',
    event = 'TermResponse',
  })
  for _, autocmd in ipairs(ok and autocmds or {}) do
    if autocmd.desc and autocmd.desc:find("'background'", 1, true) then
      pcall(vim.api.nvim_del_autocmd, autocmd.id)
    end
  end
end

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

  if p.fzf_colors then
    vim.env.FZF_DEFAULT_OPTS = FZF_BASE_OPTS .. ' --color=' .. p.fzf_colors
  end
end

vim.o.termguicolors = true
local background, ours = detect_background()
if ours then
  ignore_terminal_background()
end
vim.o.background = background

vim.cmd('colorscheme vim')
apply_highlights()

-- theme(1) sets 'background' over the rpc socket, which reloads the color
-- scheme and wipes our highlights - so hook the reload, not OptionSet, which
-- fires before it.
vim.api.nvim_create_autocmd('ColorScheme', { callback = apply_highlights })

vim.o.cursorline = true
vim.o.statusline = '%f %m%r%=Col:%c Line:%l/%L'
vim.g.c_no_curly_error = 1  -- breaks in the simplest __VA_ARGS__ macros
