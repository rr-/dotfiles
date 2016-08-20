function rotate(number)
    local rotation = mp.get_property_number('video-rotate')
    rotation = rotation + number
    rotation = rotation + 360
    rotation = rotation % 360
    mp.set_property('video-rotate', rotation)
end

mp.register_script_message('rotate', rotate)
