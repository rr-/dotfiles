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
vim.keymap.set("n", "<c-p>", require('fzf-lua').files, { desc = "Fzf files" })
vim.keymap.set("n", "<c-l>", require('fzf-lua').buffers, { desc = "Fzf open buffers" })

vim.api.nvim_create_user_command(
    'SudoSave',
    function()
        vim.cmd('w !sudo tee >/dev/null %')
    end, {}
)

require("aerial").setup({
  post_jump_cmd = "",
})
