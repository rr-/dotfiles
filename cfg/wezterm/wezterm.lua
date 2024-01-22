local wezterm = require 'wezterm'
local runtime = require 'runtime'

local config = wezterm.config_builder()

config.font = wezterm.font 'Input Mono'

config.adjust_window_size_when_changing_font_size = false
config.enable_tab_bar = false
config.window_padding = {
  left = 0,
  top = 0,
  right = 0,
  bottom = 0,
}

config.hyperlink_rules = wezterm.default_hyperlink_rules()

config.keys = {
  { key = 'Enter', mods = 'ALT', action = wezterm.action.DisableDefaultAssignment, },
  { key = 'y', mods = 'ALT', action = wezterm.action.QuickSelect },
  { key = 'u', mods = 'ALT', action = wezterm.action{
    QuickSelectArgs={
      patterns={
        "https?://\\S+"
      },
      action = wezterm.action_callback(
        function(window, pane)
          local url = window:get_selection_text_for_pane(pane)
          wezterm.log_info("opening: " .. url)
          wezterm.open_with(url)
        end
      )
    }
  }},
}

runtime.apply_to_config(config)

return config
