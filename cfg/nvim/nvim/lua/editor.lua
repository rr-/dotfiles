vim.cmd('syntax on')                        -- enable syntax highlighting

vim.opt.synmaxcol = 256                     -- highlight up to X columns (binary files)
vim.opt.number = true                       -- enable line numbers
vim.opt.relativenumber = true               -- show relative line numbers

-- show white characters
vim.opt.list = true
vim.opt.listchars = 'tab:→ ,trail:·'

-- set gutter width to 80 characters
if vim.fn.exists('+colorcolumn') == 1 then
  vim.opt.colorcolumn = '80'
end

-- whitespace settings
vim.opt.encoding = 'utf-8'                  -- character encoding of ui
vim.opt.fileencodings = 'utf-8,cp932'       -- preferred character encodings
vim.opt.fileformat = 'unix'
vim.opt.fileformats = 'unix,dos'
vim.opt.wrap = false                        -- don't wrap long lines
vim.opt.linebreak = true                    -- wrap lines at word boundaries

-- automatic aids
-- respect my choice even for ftplugin
vim.api.nvim_create_autocmd('FileType', {
  pattern = '*',
  callback = function()
    vim.opt.formatoptions:remove('t')       -- disable autowrapping text
    vim.opt.formatoptions:remove('c')       -- disable autowrapping comments
    vim.opt.formatoptions:remove('r')       -- disable inserting comment prefix after <Enter>
    vim.opt.formatoptions:remove('o')       -- disable inserting comment prefix after 'o'/'O'
    vim.opt.formatoptions:remove('j')       -- keep the comment prefix when joining lines
  end,
})

-- editor behavior
vim.opt.showcmd = true                      -- show last command in status
vim.opt.virtualedit = 'onemore'             -- allow moving cursor up to EOL+1 character
vim.opt.splitbelow = true                   -- change placement when splitting a buffer
vim.opt.splitright = true
vim.opt.shell = '/bin/zsh'                  -- when opening shell, use zsh
vim.opt.wrapscan = true                     -- search again from top if no matches
vim.opt.incsearch = false                   -- disable 'live' search
vim.opt.ignorecase = true                   -- ignore case in searches
vim.opt.smartcase = true                    -- ...unless they contain uppercase chars
vim.opt.scrolloff = 5                       -- keep at least x lines below and above cursor
vim.opt.joinspaces = false                  -- don't put double spaces when using auto wrapping
vim.opt.fillchars = 'vert:│'                -- better character for vertical window splits
vim.opt.hidden = true                       -- don't purge undo history when changing buffers
vim.opt.clipboard = 'unnamed,unnamedplus'   -- automatically copy unnamed yanks to * and +

-- miscellaneous
vim.opt.errorbells = false                  -- disable beeping
vim.opt.visualbell = false                  -- disable visual bell
vim.opt.laststatus = 2                      -- always display status line
vim.opt.modeline = true                     -- allow files to embed file-specific vim settings
vim.opt.modelines = 1                       -- ...within X lines at the top of that file

-- spellcheck
vim.opt.spell = false                       -- spell checker is off by default
vim.opt.spelllang = 'en_us,pl'              -- spell checker languages
vim.opt.spellfile = vim.fn.expand('$HOME/.config/nvim/spell/en.utf-8.add') ..
                 ',' .. vim.fn.expand('$HOME/.config/nvim/spell/pl.utf-8.add')

-- folds
vim.opt.foldenable = false                  -- disable folding
vim.opt.foldopen:remove('block')            -- { and } skips over folds
vim.opt.foldmethod = 'indent'               -- fold basing on indent (to be used with zM / zR)
vim.opt.foldnestmax = 2                     -- don't fold too deep

-- storage
-- double slash prevents file name collision, by using full file paths
vim.opt.backup = true                       -- enable backups
vim.opt.undofile = true                     -- enable persistent undo
vim.opt.undolevels = 1000                   -- store this many undo levels
vim.opt.undoreload = 10000                  -- don't wipe undo after reloading file up to 10k lines long
vim.opt.backupdir = vim.fn.expand('$HOME/.local/share/nvim/backup//') -- path to file backups

-- ignore files in commands and plugins
vim.opt.wildignore = '.hg,.git,.bzr,*.o,*.obj,*.pyc,*.pyo,__pycache__,*.swp,*.spl,*.stackdump,*~.*'
vim.opt.wildignorecase = true               -- case-insensitive filename completion in commands

-- misc
-- fix fast hitting escape + <key> being interpreted as escape sequence
vim.opt.ttimeout = true
vim.opt.ttimeoutlen = 10
vim.api.nvim_create_augroup('FastEscape', {clear = true})
vim.api.nvim_create_autocmd('InsertEnter', {
    group = group_name,
    callback = function()
        vim.opt.timeoutlen = 0
    end,
})
vim.api.nvim_create_autocmd('InsertLeave', {
    group = group_name,
    callback = function()
        vim.opt.timeoutlen = 1000
    end,
})
