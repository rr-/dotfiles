require('fzf-lua').setup(
  {
    fzf_opts = {
      ['--layout'] = "default",
    },
    grep = {
      rg_opts = "--column --line-number --no-heading --color=always --smart-case --max-columns=4096 -e",
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
