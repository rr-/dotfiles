local randomizer_list = {}
local randomizer_pos = nil
local last_playlist_count = 0

function playlist_changed(data)
    local playlist_count = mp.get_property('playlist-count')
    if playlist_count ~= last_playlist_count then
        last_playlist_count = playlist_count
        reset_randomizer()
    end
end

function random_enabled()
    return mp.get_opt('random_playback') == 'yes'
end

function reset_randomizer()
    randomizer_list = {}
    randomizer_pos = nil
end

function random_playlist_pos()
    return math.random(mp.get_property('playlist-count'))
end

function random_jump(delta)
    if randomizer_pos == nil then
        randomizer_list = {}
        table.insert(randomizer_list, random_playlist_pos())
        randomizer_pos = 1
    end

    randomizer_pos = randomizer_pos + delta

    if randomizer_pos < 1 then
        table.insert(randomizer_list, 1, random_playlist_pos())
        randomizer_pos = 1
    elseif randomizer_pos >= #randomizer_list then
        table.insert(randomizer_list, random_playlist_pos())
    end

    mp.set_property('playlist-pos', randomizer_list[randomizer_pos])
end

function file_ended(event)
    if random_enabled() and event['reason'] == 'eof' then
        random_jump(1)
    end
end

function playlist_prev()
    if random_enabled() then
        random_jump(-1)
    else
        mp.command('playlist-prev')
    end
end

function playlist_next()
    if random_enabled() then
        random_jump(1)
    else
        mp.command('playlist-next')
    end
end

mp.register_script_message('playlist-prev', playlist_prev)
mp.register_script_message('playlist-next', playlist_next)
mp.register_script_message('playlist-reset-random', reset_randomizer)
mp.register_event('end-file', file_ended)
mp.observe_property('playlist-count', nil, playlist_changed)
