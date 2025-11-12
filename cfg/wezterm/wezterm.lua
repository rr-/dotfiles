local wezterm = require 'wezterm'
local runtime = require 'runtime'
local act = wezterm.action

local config = wezterm.config_builder()

local function active_tab_index(window)
  for _, item in ipairs(window:mux_window():tabs_with_info()) do
    if item.is_active then
      return item.index
    end
  end
end

local function MoveTabRelativeWrap(dir)
  return wezterm.action_callback(function(win, pane)
    local tabs = win:mux_window():tabs()
    local idx = active_tab_index(win)
    local new = (idx + dir) % #tabs
    win:perform_action(act.MoveTab(new), pane)
  end)
end

config.background = {
  {
    source = {
      File = '/home/dash/.config/wezterm/stardust-light.png',
    },
    width = '700',
    height = '700',
  },
}

config.window_decorations = "NONE"
config.font = wezterm.font 'Input Mono'

config.adjust_window_size_when_changing_font_size = false
config.hide_tab_bar_if_only_one_tab = true
config.enable_tab_bar = true
config.use_fancy_tab_bar = false
config.window_padding = {
  left = 0,
  top = 0,
  right = 0,
  bottom = 0,
}

config.warn_about_missing_glyphs = false
config.hyperlink_rules = wezterm.default_hyperlink_rules()

local function isInVim(pane)
  local proc = pane:get_foreground_process_name()
  return proc and proc:match('n?vim')
end

local function conditionalActivatePane(win, pane, pane_direction, vim_direction)
  local vim_pane_changed = false

  if isInVim(pane) then
    local before = pane:get_cursor_position()
    win:perform_action(act.SendKey{key=vim_direction, mods='ALT'}, pane)
    wezterm.sleep_ms(50)
    local after = pane:get_cursor_position()

    if before.x ~= after.x and before.y ~= after.y then
      vim_pane_changed = true
    end
  end

  if not vim_pane_changed then
    win:perform_action(act.ActivatePaneDirection(pane_direction), pane)
  end
end

wezterm.on('ActivatePaneDirection-right', function(win, pane)
    conditionalActivatePane(win, pane, 'Right', 'l')
end)
wezterm.on('ActivatePaneDirection-left', function(win, pane)
    conditionalActivatePane(win, pane, 'Left', 'h')
end)
wezterm.on('ActivatePaneDirection-up', function(win, pane)
    conditionalActivatePane(win, pane, 'Up', 'k')
end)
wezterm.on('ActivatePaneDirection-down', function(win, pane)
    conditionalActivatePane(win, pane, 'Down', 'j')
end)

-- config.leader = { key = 'a', mods = 'CTRL', timeout_milliseconds = 1000 }
config.keys = {
  -- -- send leader back to terminal
  -- { key = 'b', mods = 'LEADER|CTRL', action = act.SendKey { key = 'a', mods = 'CTRL' } },
  -- -- split horizontal
  -- { key = 'v', mods = 'LEADER', action = act.SplitHorizontal { domain = 'CurrentPaneDomain' } },
  -- -- split horizontal
  -- { key = 's', mods = 'LEADER', action = act.SplitVertical { domain = 'CurrentPaneDomain' } },
  -- -- rotate counter clockwise
  -- { key = '{', mods = 'LEADER|SHIFT', action = act.RotatePanes 'CounterClockwise' },
  -- -- rotate clockwise
  -- { key = '}', mods = 'LEADER|SHIFT', action = act.RotatePanes 'Clockwise' },
  -- -- create tab at the end
  -- { key = 'c', mods = 'LEADER', action = wezterm.action_callback(function(win, pane)
  --     win:mux_window():spawn_tab({ cwd = pane:get_current_working_dir().file_path })
  --   end) },
  -- -- create tab next to current
  -- { key = 'c', mods = 'LEADER|CTRL', action = wezterm.action_callback(function(win, pane)
  --     local active_tab_index = active_tab_index(win)
  --     win:mux_window():spawn_tab({ cwd = pane:get_current_working_dir().file_path })
  --     win:perform_action(act.MoveTab(active_tab_index + 1), pane)
  --   end) },
  -- -- select next tab
  -- { key = 'n', mods = 'LEADER', action = act.ActivateTabRelative(1) },
  -- { key = 'n', mods = 'LEADER|CTRL', action = act.ActivateTabRelative(1) },
  -- { key = 'n', mods = 'ALT', action = act.ActivateTabRelative(1) },
  -- -- select previous tab
  -- { key = 'p', mods = 'LEADER', action = act.ActivateTabRelative(-1) },
  -- { key = 'p', mods = 'LEADER|CTRL', action = act.ActivateTabRelative(-1) },
  -- { key = 'p', mods = 'ALT', action = act.ActivateTabRelative(-1) },
  -- -- select tab in given direction
  -- { key = 'h', mods = 'LEADER', action = act.ActivatePaneDirection 'Left' },
  -- { key = 'l', mods = 'LEADER', action = act.ActivatePaneDirection 'Right' },
  -- { key = 'k', mods = 'LEADER', action = act.ActivatePaneDirection 'Up' },
  -- { key = 'j', mods = 'LEADER', action = act.ActivatePaneDirection 'Down' },
  -- -- resize pane
  -- { key = 'H', mods = 'ALT|SHIFT', action = act.AdjustPaneSize { 'Left', 5 } },
  -- { key = 'J', mods = 'ALT|SHIFT', action = act.AdjustPaneSize { 'Down', 5 } },
  -- { key = 'K', mods = 'ALT|SHIFT', action = act.AdjustPaneSize { 'Up', 5 } },
  -- { key = 'L', mods = 'ALT|SHIFT', action = act.AdjustPaneSize { 'Right', 5 } },
  -- -- switch to n-th tab
  -- { key = '1', mods = 'ALT', action = act.ActivateTab(0) },
  -- { key = '2', mods = 'ALT', action = act.ActivateTab(1) },
  -- { key = '3', mods = 'ALT', action = act.ActivateTab(2) },
  -- { key = '4', mods = 'ALT', action = act.ActivateTab(3) },
  -- { key = '5', mods = 'ALT', action = act.ActivateTab(4) },
  -- { key = '6', mods = 'ALT', action = act.ActivateTab(5) },
  -- { key = '7', mods = 'ALT', action = act.ActivateTab(6) },
  -- { key = '8', mods = 'ALT', action = act.ActivateTab(7) },
  -- { key = '9', mods = 'ALT', action = act.ActivateTab(8) },
  -- { key = '0', mods = 'ALT', action = act.ActivateTab(9) },
  -- { key = 'h', mods = 'ALT', action = act.EmitEvent('ActivatePaneDirection-left') },
  -- { key = 'j', mods = 'ALT', action = act.EmitEvent('ActivatePaneDirection-down') },
  -- { key = 'k', mods = 'ALT', action = act.EmitEvent('ActivatePaneDirection-up') },
  -- { key = 'l', mods = 'ALT', action = act.EmitEvent('ActivatePaneDirection-right') },
  -- { key = 'F11', action = act.PaneSelect },
  -- { key = '[', mods = 'LEADER', action = act.ActivateCopyMode },
  -- --{ key = ']', mods = 'LEADER', action = act.PasteFrom 'PrimarySelection' },
  -- { key = ']', mods = 'LEADER', action = act.PasteFrom 'Clipboard' },

  -- -- F12: choose-tree -ZswOname → switch workspace
  -- {key="F12", action=wezterm.action.ShowLauncherArgs{ flags="WORKSPACES|TABS" }},

  -- Ctrl-w: rename window (like 'rename-window')
  {key="w", mods="LEADER|CTRL", action=wezterm.action.PromptInputLine{
    description = "New pane name:",
    action = wezterm.action_callback(function(window, pane, line)
      if line then
        window:active_tab():set_title(line)
      end
    end),
  }},

  -- move active tab left/right
  { key = 'LeftArrow',  mods = 'LEADER', action = MoveTabRelativeWrap(-1) },
  { key = 'RightArrow', mods = 'LEADER', action = MoveTabRelativeWrap(1) },

  { key = 'L', mods = 'CTRL', action = act.ShowDebugOverlay },
  { key = 'V', mods = 'CTRL|SHIFT', action = act.PasteFrom 'PrimarySelection', },
  { key = 'Enter', mods = 'ALT', action = act.DisableDefaultAssignment, },
  { key = 'y', mods = 'ALT', action = act.QuickSelect },
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
