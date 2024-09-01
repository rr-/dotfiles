-- ----------------------------------------
-- indentation settings
-- ----------------------------------------

vim.opt.expandtab = true        -- use spaces instead of tab
vim.opt.tabstop = 4             -- spaces that tab counts for
vim.opt.softtabstop = 4         -- spaces that tab counts for in edit mode
vim.opt.shiftwidth = 4          -- spaces for each step of auto-indent

-- fast indentation styles for working with other people's projects
vim.api.nvim_create_user_command('TwoSpaces', function()
    vim.opt.expandtab = true
    vim.opt.softtabstop = 2
    vim.opt.tabstop = 2
    vim.opt.shiftwidth = 2
end, {})

vim.api.nvim_create_user_command('FourSpaces', function()
    vim.opt.expandtab = true
    vim.opt.softtabstop = 4
    vim.opt.tabstop = 4
    vim.opt.shiftwidth = 4
end, {})

vim.api.nvim_create_user_command('Tabs', function()
    vim.opt.expandtab = false
    vim.opt.softtabstop = 4
    vim.opt.tabstop = 4
    vim.opt.shiftwidth = 4
end, {})

vim.opt.autoindent = true       -- match indentation from previous line after <CR>
vim.opt.smartindent = false     -- don't add any extra indentation after { (I)
vim.opt.cindent = false         -- don't add any extra indentation after { (II)

vim.cmd('filetype plugin on')   -- enable filetype specific stuff
vim.cmd('filetype indent off')  -- but disable indentation settings
