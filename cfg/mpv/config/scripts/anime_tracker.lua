local msg = require("mp.msg")
local utils = require("mp.utils")

local WATCH_THRESHOLD = 0.7
local last_path = nil
local last_time_pos = 0
local last_duration = 0

local function is_url(path)
  return path:match("^%a[%w+.-]*://") ~= nil
end

local function resolve_full_path(path)
  if path == nil or path == "" then
    return nil
  end

  if is_url(path) then
    return nil
  end

  if path:sub(1, 1) == "/" or path:match("^%a:[/\\]") then
    return path
  end

  local working_directory = mp.get_property("working-directory")
  if not working_directory or working_directory == "" then
    return path
  end

  return utils.join_path(working_directory, path)
end

local function should_track(full_path, time_pos, duration)
  if not full_path then
    return false
  end

  if not full_path:lower():find("anime", 1, true) then
    return false
  end

  if not duration or duration <= 0 then
    return false
  end

  if not time_pos or time_pos <= 0 then
    return false
  end

  local watched_ratio = time_pos / duration
  return watched_ratio > WATCH_THRESHOLD
end

local function on_shutdown()
  local full_path = resolve_full_path(mp.get_property("path") or last_path)
  local time_pos = mp.get_property_number("time-pos", 0)
  local duration = mp.get_property_number("duration", 0)

  if time_pos <= 0 then
    time_pos = last_time_pos
  end
  if duration <= 0 then
    duration = last_duration
  end

  if not should_track(full_path, time_pos, duration) then
    msg.debug("anime_tracker: not tracking this file")
    return
  end

  local result = mp.command_native({
    name = "subprocess",
    playback_only = false,
    detach = true,
    args = { "anime-tracker", full_path },
  })

  if result and result.status and result.status ~= 0 then
    msg.warn(("anime-tracker failed with status %s"):format(tostring(result.status)))
    return
  end

  msg.info(("anime_tracker: tracked %s"):format(full_path))
end

mp.observe_property("path", "string", function(_, value)
  if value and value ~= "" then
    last_path = value
  end
end)

mp.observe_property("time-pos", "number", function(_, value)
  if value and value > 0 then
    last_time_pos = value
  end
end)

mp.observe_property("duration", "number", function(_, value)
  if value and value > 0 then
    last_duration = value
  end
end)

msg.info("anime_tracker: script loaded")
mp.register_event("shutdown", on_shutdown)
