local on = mp.get_opt('images-statusbar') == 'yes'

function update_statusbar()
    if on == true then
        local playlist_pos = tonumber(mp.get_property('playlist-pos')) + 1
        local playlist_count = tonumber(mp.get_property('playlist-count'))
        local path = mp.get_property('filename')
        mp.set_property(
            'options/osd-msg1',
            string.format(
                '%s (%d/%d)',
                path,
                playlist_pos,
                playlist_count))
    end
end

function toggle_statusbar()
    if on == false then
        on = true
        update_statusbar()
    else
        on = false
        mp.set_property('options/osd-msg1', '')
    end
    mp.resume_all()
end

mp.register_event('file-loaded', update_statusbar)
mp.register_script_message('toggle-statusbar', toggle_statusbar)
