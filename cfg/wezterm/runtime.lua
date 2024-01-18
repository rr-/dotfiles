local wezterm = require 'wezterm'
local module = {}
function module.apply_to_config(config)
  config.color_scheme = 'dash_light'
  config.dpi = 96
end
return module
