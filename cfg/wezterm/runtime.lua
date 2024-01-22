local wezterm = require 'wezterm'
local module = {}
function module.apply_to_config(config)
  config.color_scheme = 'dash_light'
  config.font_size = 11
end
return module
