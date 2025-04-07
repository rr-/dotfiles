local wezterm = require 'wezterm'
local module = {}
function module.apply_to_config(config)
  config.color_scheme = 'dash_light'
  if config.background.source ~= nil then
    config.background.source.File = '/home/dash/.config/wezterm/stardust-light.png'
  end
  config.font_size = 11
end
return module
