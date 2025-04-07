function ConvertToBinary()
  local word = vim.fn.expand("<cword>")

  -- Determine if the word is a hex or decimal number
  local num
  if word:match("^0x") then
    num = tonumber(word, 16)
  elseif word:match("^%d+$") then
    num = tonumber(word)
  end

  if not num then
    print("Not a valid number")
    return
  end

  -- Convert to binary string manually
  local binary = ""
  while num > 0 do
    binary = tostring(num % 2) .. binary
    num = math.floor(num / 2)
  end

  -- Ensure the length is a multiple of 8
  local length = math.ceil(#binary / 8) * 8
  binary = string.rep("0", length - #binary) .. binary

  -- Add ' separators every 8 bits
  binary = binary:gsub("(%d%d%d%d%d%d%d%d)", "%1'"):gsub("'$", "")
  local result = "0b" .. binary

  -- Replace the word with the binary representation
  vim.fn.setline('.', vim.fn.substitute(vim.fn.getline('.'), '\\V' .. vim.fn.escape(word, '\\'), result, ''))
end



function ConvertToHex()
  local word = vim.fn.expand("<cword>")

  -- Determine if the word is a hex or decimal number
  local num
  if word:match("^0x") then
    num = tonumber(word, 16)
  elseif word:match("^%d+$") then
    num = tonumber(word)
  end

  if not num then
    print("Not a valid number")
    return
  end

  -- Convert to hexadecimal string
  local hex = string.format("0x%X", num)

  -- Replace the word with the hexadecimal representation
  vim.fn.setline('.', vim.fn.substitute(vim.fn.getline('.'), '\\V' .. vim.fn.escape(word, '\\'), hex, ''))
end



function insert_lua_expression()
    local expression = vim.fn.input("Enter Lua expression: ")
    local ok, result = pcall(load("return " .. expression))
    if ok then
        vim.api.nvim_put({tostring(result)}, 'c', true, true)
    else
        print("Error evaluating expression.")
    end
end



local function pass_through_chatgpt(opts)
  local start_pos = vim.api.nvim_buf_get_mark(0, '<')
  local end_pos = vim.api.nvim_buf_get_mark(0, '>')
  if start_pos[1] == 0 or end_pos[1] == 0 then
    print("Selection markers not set.")
    return
  end

  -- handle v:maxcol
  local start_line = vim.api.nvim_buf_get_lines(0, start_pos[1]-1, start_pos[1], false)[1]
  local end_line = vim.api.nvim_buf_get_lines(0, end_pos[1]-1, end_pos[1], false)[1]

  if start_pos[2] > #start_line then
    start_pos[2] = #start_line
  end
  if end_pos[2] > #end_line then
    end_pos[2] = #end_line
  end

  local lines = vim.api.nvim_buf_get_lines(0, start_pos[1] - 1, end_pos[1], true)
  local input_text = table.concat(lines, '\n')

  local cmd = {'ai', '-c', string.format('input: raw code, output: raw code. %s', opts.args)}
  --cmd = {'zsh', '-c', 'echo witam; sleep 1; echo foo'}

  local output_buffer = {}
  local opts = {
    text = true,
    stdin = input_text,
    stdout = function(err, output_text)
      if err then
        print("Error: ", err)
        return
      end
      if output_text ~= nil then
        table.insert(output_buffer, output_text)
      end
    end,
  }

  vim.system(cmd, opts, function()
    local complete_output = table.concat(output_buffer)

    vim.schedule(function()
      vim.api.nvim_buf_set_text(
        0,
        start_pos[1] - 1,
        start_pos[2],
        end_pos[1] - 1,
        end_pos[2],
        vim.split(complete_output, '\n')
      )
    end)
  end):wait()
end



vim.api.nvim_create_user_command('AI', pass_through_chatgpt, { range = true, nargs = 1 })
vim.api.nvim_set_keymap('n', '<leader>b', ':lua ConvertToBinary()<CR>', { noremap = true, silent = true })
vim.api.nvim_set_keymap('n', '<leader>x', ':lua ConvertToHex()<CR>', { noremap = true, silent = true })
vim.api.nvim_set_keymap('n', '<Leader>ev', [[:lua insert_lua_expression()<CR>]], { noremap = true, silent = true })
