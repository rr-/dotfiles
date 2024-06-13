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

config.warn_about_missing_glyphs = false
config.hyperlink_rules = wezterm.default_hyperlink_rules()

config.keys = {
  { key = 'V', mods = 'CTRL|SHIFT', action = wezterm.action.PasteFrom 'PrimarySelection', },
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

wezterm.on('user-var-changed', function(window, pane, name, value)
    local overrides = window:get_config_overrides() or {}
    if name == "ZEN_MODE" then
        local incremental = value:find("+")
        local number_value = tonumber(value)
        if incremental ~= nil then
            while (number_value > 0) do
                window:perform_action(wezterm.action.IncreaseFontSize, pane)
                number_value = number_value - 1
            end
        elseif number_value < 0 then
            window:perform_action(wezterm.action.ResetFontSize, pane)
            overrides.font_size = nil
        else
            overrides.font_size = number_value
        end
    end
    window:set_config_overrides(overrides)
end)

return config
