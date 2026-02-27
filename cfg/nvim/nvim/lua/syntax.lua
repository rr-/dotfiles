vim.api.nvim_create_autocmd("BufReadPost", {
  pattern = "*.txt",
  callback = function()
    if vim.fn.search("seed_control\\|config gameplay", "nw") ~= 0 then
      vim.bo.filetype = "trx_replays"
    end
  end,
})
