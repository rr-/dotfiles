local wezterm = require 'wezterm'
local module = {}
function module.apply_to_config(config)
  config.color_scheme = 'dash_light'
  -- config.background is a list of layers, so the image lives on the first
  -- one; config.background.source is always nil and silently skips the swap
  local layer = config.background and config.background[1]
  if layer ~= nil then
    layer.source.File = '/home/dash/.config/wezterm/stardust-light.png'
  end
  config.font_size = 11
end
return module
