local reset_view_after_file_change = mp.get_opt('reset-view') == 'yes'

function reset_panscan()
    props = {'video-pan-x', 'video-pan-y', 'video-zoom', 'video-rotate'}
    for _, prop in pairs(props) do
        if mp.get_property_number(prop) ~= 0 then
            mp.set_property_number(prop, 0)
        end
    end
end

function file_changed()
    if reset_view_after_file_change then
        reset_panscan()
    end
end

function view_pixel()
    mp.set_property_number('video-pan-x', 0)
    mp.set_property_number('video-pan-y', 0)
    mp.set_property_number('video-zoom', 3)
    mp.set_property_number('video-rotate', 0)
    mp.set_property_number('panscan', 0)
    mp.set_property_bool('video-unscaled', true)
    mp.set_property('scale', 'nearest')
    mp.set_property('sws-scaler', 'point')
    mp.commandv('show-text', "Pixel view")
end

function view_normal()
    mp.set_property_number('video-pan-x', 0)
    mp.set_property_number('video-pan-y', 0)
    mp.set_property_number('video-rotate', 0)
    mp.set_property_number('video-zoom', 0)
    mp.set_property_number('panscan', 0)
    mp.set_property_bool('video-unscaled', false)
    mp.set_property('scale', 'lanczos')
    mp.set_property('sws-scaler', 'lanczos')
    mp.commandv('show-text', "Normal view")
end

function view_fit_window()
    mp.set_property_number('video-pan-x', 0)
    mp.set_property_number('video-pan-y', 0)
    mp.set_property_number('video-zoom', 0)
    mp.set_property_number('video-rotate', 0)
    mp.set_property_number('panscan', 0)
    mp.set_property_bool('video-unscaled', false)
    mp.commandv('show-text', "Fit to window")
end

function view_fill_window()
    mp.set_property_number('video-pan-x', 0)
    mp.set_property_number('video-pan-y', 0)
    mp.set_property_number('video-zoom', 0)
    mp.set_property_number('video-rotate', 0)
    mp.set_property_number('panscan', 1)
    mp.set_property_bool('video-unscaled', false)
    mp.commandv('show-text', "Fill window")
end

function view_original()
    mp.set_property_number('video-pan-x', 0)
    mp.set_property_number('video-pan-y', 0)
    mp.set_property_number('video-zoom', 0)
    mp.set_property_number('video-rotate', 0)
    mp.set_property_number('panscan', 0)
    mp.set_property_bool('video-unscaled', true)
    mp.commandv('show-text', "Original scale")
end

function zoom_change(delta)
    mp.set_property_number('video-zoom', mp.get_property_number('video-zoom') + delta)
    mp.commandv('show-text', string.format('Zoom: %.3f', mp.get_property_number('video-zoom')))
end

function pan_x(delta)
    mp.set_property_number('video-pan-x', mp.get_property_number('video-pan-x') + delta)
    mp.commandv('show-text', string.format('X: %.3f', mp.get_property_number('video-pan-x')))
end

function pan_y(delta)
    mp.set_property_number('video-pan-y', mp.get_property_number('video-pan-y') + delta)
    mp.commandv('show-text', string.format('Y: %.3f', mp.get_property_number('video-pan-y')))
end

function zoom_in()
    zoom_change(0.03)
end

function zoom_out()
    zoom_change(-0.03)
end

function pan(dir, multiplier)
    delta = 0.01 * (multiplier or 1)
    if dir == 'up' then
        pan_y(delta)
    elseif dir == 'down' then
        pan_y(-delta)
    elseif dir == 'left' then
        pan_x(delta)
    elseif dir == 'right' then
        pan_x(-delta)
    end
end

function rotate(number)
    local rotation = mp.get_property_number('video-rotate')
    rotation = rotation + number
    rotation = rotation + 360
    rotation = rotation % 360
    mp.set_property('video-rotate', rotation)
end

mp.register_script_message('view-pixel', view_pixel)
mp.register_script_message('view-normal', view_normal)
mp.register_script_message('view-fit-window', view_fit_window)
mp.register_script_message('view-fill-window', view_fill_window)
mp.register_script_message('view-original', view_original)
mp.register_script_message('zoom-in', zoom_in)
mp.register_script_message('zoom-out', zoom_out)
mp.register_script_message('pan', pan)
mp.register_script_message('rotate', rotate)
mp.register_event('end-file', file_changed)
