local on = mp.get_opt('reset-zoom') == 'yes'

function file_changed()
    if on == true then
        mp.set_property('video-unscaled', 'no')
        mp.set_property_number('video-pan-x', 0)
        mp.set_property_number('video-pan-y', 0)
        mp.set_property_number('video-zoom', 0)
        mp.set_property_number('video-rotate', 0)
    end
end

mp.register_event('end-file', file_changed)
