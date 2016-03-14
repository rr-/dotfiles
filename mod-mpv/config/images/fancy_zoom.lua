local rotation = 0
local rendering = false
local user_fiddled = false

math.sign = math.sign or function(x) return x<0 and -1 or x>0 and 1 or 0 end

function get(property)
    return mp.get_property(property)
end

function set(property, value)
    mp.set_property(property, value)
end

function add(property, delta)
    set(property, get(property) + delta)
end

function add_rotation(delta)
    rotation = rotation + delta
    rotation = rotation + 360
    rotation = rotation % 360
    if rotation == 0 then
        mp.command('vf set ""')
    else
        mp.command('vf set rotate=' .. rotation)
    end
end

function get_real_scale()
    local video = {
        width  = get('video-params/dw'),
        height = get('video-params/dh'),
    }
    local window = {
        width  = get('osd-width'),
        height = get('osd-height'),
    }
    if video.width == nil or window.width == nil then return nil end
    video.width  = tonumber(video.width)
    video.height = tonumber(video.height)
    window.width  = tonumber(window.width)
    window.height = tonumber(window.height)
    if window.width / window.height < video.width / video.height then
        return window.width / video.width
    else
        return window.height / video.height
    end
end

function reset_other_settings()
    set('video-pan-x', 0)
    set('video-pan-y', 0)
    set('video-aspect', 0)
end

function correct_pan_for_dimension(dimension, delta)
    value = tonumber(get('video-pan-' .. dimension))
    if dimension == 'x' then
        window_size = tonumber(get('osd-width'))
        video_size = tonumber(get('video-params/dw'))
    else
        window_size = tonumber(get('osd-height'))
        video_size = tonumber(get('video-params/dh'))
    end
    window_scale = get_real_scale()
    zoom_scale = tonumber(get('video-zoom')) + 1

    -- what a bunch of crap
    actual_canvas_size = video_size * window_scale * zoom_scale
    if actual_canvas_size < window_size then
        set('video-pan-' .. dimension, 0)
    elseif (1 - math.abs(value) * 2) * actual_canvas_size < window_size then
        value = math.sign(value) * (-(window_size / actual_canvas_size - 1) / 2)
        set('video-pan-' .. dimension, value)
    end
end

function correct_pan()
    correct_pan_for_dimension('x', 0)
    correct_pan_for_dimension('y', 0)
end

function scale_original()
    local window_scale = get_real_scale()
    if window_scale == nil then return end
    local target_scale = (1 / window_scale) - 1
    reset_other_settings()
    set('video-zoom', target_scale)
    correct_pan()
end

function scale_arbitrary(multiplier)
    local window_scale = get_real_scale()
    if window_scale == nil then return end
    local target_scale = ((1 / window_scale * multiplier) - 1)
    reset_other_settings()
    set('video-zoom', target_scale)
    correct_pan()
end

function scale_to_window()
    reset_other_settings()
    set('video-zoom', 0)
    correct_pan()
end

function fit_to_window()
    local window_scale = get_real_scale()
    if window_scale == nil then return end
    if window_scale > 1 then
        scale_original()
    else
        scale_to_window()
    end
end

function file_changed()
    user_fiddled = false
    rendering = true
end

function file_rendered()
    -- https://github.com/mpv-player/mpv/pull/2936
    if rendering then
        rendering = false
        fit_to_window()
    end
end

function window_size_changed()
    if not rendering and not user_fiddled then
        fit_to_window()
    end
end

mp.add_hook('on_prerender', 50, file_rendered)
mp.observe_property('osd-width', int, window_size_changed)
mp.register_event('file-loaded', file_changed)
mp.register_event('video-reconfig', window_size_changed)
mp.register_script_message('fit-to-window', function() fit_to_window(); user_fiddled = true; end)
mp.register_script_message('fit-original',  function() scale_original(); user_fiddled = true; end)
mp.register_script_message('set-zoom',      function(v) scale_arbitrary(v); user_fiddled = true; end)
mp.register_script_message('zoom-out',      function(d) add('video-zoom', -d); correct_pan(); user_fiddled = true; end)
mp.register_script_message('zoom-in',       function(d) add('video-zoom', d); correct_pan(); user_fiddled = true; end)
mp.register_script_message('pan-x',         function(d) add('video-pan-x', d); correct_pan(); user_fiddled = true; end)
mp.register_script_message('pan-y',         function(d) add('video-pan-y', d); correct_pan(); user_fiddled = true; end)
mp.register_script_message('aspect',        function(d) add('video-aspect', d); correct_pan(); user_fiddled = true; end)
mp.register_script_message('rotate',        function(d) add_rotation(d); user_fiddled = true; end)
