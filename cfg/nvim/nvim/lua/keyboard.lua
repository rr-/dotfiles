----------------------------------------
-- keyboard bindings
----------------------------------------

local map = vim.keymap.set
vim.g.mapleader = vim.api.nvim_replace_termcodes('<BS>', false, false, true)

-- movement over visual lines, not physical lines
map('n', 'k', 'gk', { buffer = true, silent = true })
map('n', 'j', 'gj', { buffer = true, silent = true })
map('n', 'gk', 'k', { buffer = true, silent = true })
map('n', 'gj', 'j', { buffer = true, silent = true })

-- ctrl+s = save
map('i', '<C-s>', '<Esc>:update<CR>', { silent = true })
map('n', '<C-s>', ':update<CR>', { silent = true })

-- ctrl+c = copy
map('i', '<C-c>', '<Esc>"+y', { silent = true })
map('n', '<C-c>', '"+y', { silent = true })

-- ctrl+q = close window
map('i', '<C-q>', '<Esc>:q<CR>', { silent = true })
map('n', '<C-q>', ':q<CR>', { silent = true })

-- ctrl+w ctrl+m = open new file vertically
map('n', '<C-w><C-m>', ':vne<CR>', { silent = true })
map('n', '<C-w>m', ':vne<CR>', { silent = true })

-- disable stupid manual pages
map('n', 'K', '<nop>', { silent = true })
map('v', 'K', '<nop>', { silent = true })

-- easier formatting of paragraphs
map('v', 'Q', 'gq', { silent = true })
map('n', 'Q', 'gqap', { silent = true })

-- convenient new tab
map('n', 'gn', ':tabnew<CR>', { silent = true })

-- go to line
map('n', '<CR>', 'v:count == 0 ? "<CR>" : ":<C-U><Esc>" .. v:count .. "G"', {expr = true, silent = true})

-- quickfix navigation
map('n', '<M-c>', ':cn<CR>', { silent = true })
map('n', '<M-C>', ':cp<CR>', { silent = true })

-- exit terminal mode via escape
map('t', '<Esc>', '<C-\\><C-n>', { silent = true })

-- file explorer
map('i', '<F3>', '<Esc>:Fern %:h -reveal=%:p<CR>', { silent = true })
map('n', '<F3>', ':Fern %:h -reveal=%:p<CR>', { silent = true })

-- EasyAlign
map('n', 'ga', '<Plug>(EasyAlign)', {})
map('x', 'ga', '<Plug>(EasyAlign)', {})

-- readline emulation
map('c', '<C-a>', '<Home>', { noremap = true })
map('c', '<C-e>', '<End>', { noremap = true })
map('c', '<C-b>', '<Left>', { noremap = true })
map('c', '<C-f>', '<Right>', { noremap = true })
map('c', '<C-p>', '<Up>', { noremap = true })
map('c', '<C-n>', '<Down>', { noremap = true })
map('c', '<C-d>', '<Del>', { noremap = true })
map('c', '<C-k>', '<C-\\>e getcmdpos() == 1 and \'\' or getcmdline()[:getcmdpos()-2]<CR>', { noremap = true })
map('c', '<M-b>', '<S-Left>', { noremap = true })
map('c', '<M-f>', '<S-Right>', { noremap = true })

-- Aerial
map("n", "<M-[>", "<cmd>AerialPrev<CR>", { buffer = bufnr })
map("n", "<M-]>", "<cmd>AerialNext<CR>", { buffer = bufnr })
map("n", "<leader>a", "<cmd>AerialToggle!<CR>")

-- inoreabbr <expr> ts# strftime("%Y-%m-%d")
vim.cmd [[inoreabbr <expr> ts# strftime("%Y-%m-%d")]]


