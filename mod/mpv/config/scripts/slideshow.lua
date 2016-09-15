local on = false
local expected_playlist_pos  = 0
local timer = nil

function get_playlist_pos()
    return mp.get_property_number('playlist-pos') + 1
end

function get_playlist_count()
    return mp.get_property_number('playlist-count')
end

function queue_next_slide()
    local next_slide = function()
        if (get_playlist_pos() == get_playlist_count()) or
                (get_playlist_pos() ~= expected_playlist_pos) then
            stop_slideshow()
        else
            mp.command('playlist_next')
        end
    end
    if timer then
        timer:kill()
    end
    timer = mp.add_timeout(0.5, next_slide)
end

function start_slideshow()
    if get_playlist_pos() == get_playlist_count() then
        mp.osd_message('Can\'t start slideshow on last file')
        return
    end
    mp.osd_message('Slideshow started')
    on = true
    queue_next_slide()
    expected_playlist_pos = get_playlist_pos()
end

function stop_slideshow()
    if not on then
        return
    end
    mp.osd_message('Slideshow stopped')
    on = false
    timer:kill()
end

function toggle_slideshow()
    if on then
        stop_slideshow()
    else
        start_slideshow()
    end
end

function file_loaded()
    if on then
        expected_playlist_pos = expected_playlist_pos + 1
        queue_next_slide()
    end
end

mp.register_event('file-loaded', file_loaded)
mp.register_script_message('toggle-slideshow', toggle_slideshow)
