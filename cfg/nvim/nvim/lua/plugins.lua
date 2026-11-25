local actions = require "fzf-lua.actions"

local M = {}

M.file_edit_and_qf = function(selected, opts)
  if #selected > 1 then
    local result = actions.file_sel_to_qf(selected, opts)
    vim.cmd('cfirst')
    return result
  end
  return actions.file_edit(selected, opts)
end

vim.g['fern#hide_cursor'] = 0

require('fzf-lua').setup(
  {
    fzf_opts = {
      ['--layout'] = "default",
    },
    grep = {
      rg_opts = "--column --line-number --no-heading --color=always --smart-case --max-columns=4096 -e",
    },
    actions = {
      files = {
        true,
        ["enter"] = M.file_edit_and_qf,
      },
    },
    keymap = {
      fzf = {
        true,
        ["ctrl-b"] = "backward-char",
        ["ctrl-f"] = "forward-char",
        ["ctrl-u"] = "unix-line-discard+kill-line",
      },
    },
  }
)

vim.keymap.set("n", "<c-e>", function()
  require('fzf-lua').grep_project({ fzf_opts = { ["--nth"] = false } })
end, { desc = "Fzf grep" })
vim.keymap.set("n", "<m-e>", function()
  require('fzf-lua').live_grep_native({ fzf_opts = { ["--nth"] = false } })
end, { desc = "Fzf grep" })
vim.keymap.set("n", "<c-p>", require('fzf-lua').files, { desc = "Fzf files" })
vim.keymap.set("n", "<c-l>", require('fzf-lua').buffers, { desc = "Fzf open buffers" })

local map = vim.keymap.set

-- file explorer
map('i', '<F3>', '<Esc>:Fern %:h -reveal=%:p<CR>', { silent = true })
map('n', '<F3>', ':Fern %:h -reveal=%:p<CR>', { silent = true })
map('n', '<leader>k', ':Fern %:h -reveal=%:p<CR>', { silent = true })

-- EasyAlign
map('n', 'ga', '<Plug>(EasyAlign)', {})
map('x', 'ga', '<Plug>(EasyAlign)', {})

-- Aerial
map("n", "<M-[>", "<cmd>AerialPrev<CR>")
map("n", "<M-]>", "<cmd>AerialNext<CR>")
map("n", "<leader>a", "<cmd>AerialToggle!<CR>")

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

require("aerial").setup({
  post_jump_cmd = "",
})
