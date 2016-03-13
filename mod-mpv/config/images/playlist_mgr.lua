function prev_file()
    mp.command('playlist-prev')
end

function next_file()
    mp.command('playlist-next')
end

function first_file()
    mp.set_property('playlist-pos', 0)
end

function last_file()
    mp.set_property('playlist-pos', mp.get_property('playlist-count') - 1)
end

mp.register_script_message('first-file', first_file)
mp.register_script_message('prev-file', prev_file)
mp.register_script_message('next-file', next_file)
mp.register_script_message('last-file', last_file)
