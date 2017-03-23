local on = mp.get_opt('reset-view') == 'yes'

function file_changed()
    if not on then
        return
    end

    props = {'video-pan-x', 'video-pan-y', 'video-zoom', 'video-rotate'}
    for _, prop in pairs(props) do
        if mp.get_property_number(prop) ~= 0 then
            mp.set_property_number(prop, 0)
        end
    end
end

mp.register_event('end-file', file_changed)
