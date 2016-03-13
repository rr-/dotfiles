local on = false
local expected_pos = 0
local timer = nil

function next_slide()
    mp.command('playlist_next')
end

function start_slideshow()
    local playlist_pos = tonumber(mp.get_property('playlist-pos')) + 1
    local playlist_count = tonumber(mp.get_property('playlist-count'))
    if playlist_pos == playlist_count then
        mp.osd_message('Can\'t start slideshow on last file')
        return
    end
    expected_pos = playlist_pos + 1
    mp.osd_message('Slideshow started')
    on = true
    if timer then
        timer:resume()
    else
        timer = mp.add_periodic_timer(0.5, next_slide)
    end
end

function stop_slideshow()
    mp.osd_message('Slideshow stopped')
    on = false
    timer:kill()
end

function toggle_slideshow()
    if on == false then
        start_slideshow()
    else
        stop_slideshow()
    end
end

function file_loaded()
    local playlist_pos = tonumber(mp.get_property('playlist-pos')) + 1
    local playlist_count = tonumber(mp.get_property('playlist-count'))
    if on then
        if playlist_pos == playlist_count or playlist_pos ~= expected_pos then
            stop_slideshow()
        else
            expected_pos = playlist_pos + 1
        end
    end
end

mp.register_event('file-loaded', file_loaded)
mp.register_script_message('toggle-slideshow', toggle_slideshow)
