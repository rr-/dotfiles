mputils = require 'mp.utils'
require 'os'

-- from shell.lua, by Peter Odding
local function escape(...)
    local command = type(...) == 'table' and ... or { ... }
    for i, s in ipairs(command) do
        s = (tostring(s) or ''):gsub('"', '\\"')
        if s:find '[^A-Za-z0-9_."/-]' then
            s = '"' .. s .. '"'
        elseif s == '' then
            s = '""'
        end
        command[i] = s
    end
    return table.concat(command, ' ')
end

function trim(path)
    return string.match(path, '^%s*(.-)%s*$')
end

function run(t)
    return trim(mputils.subprocess(t).stdout)
end

function on_path_change(_, new_path)
    last_file_path = new_path
end

function on_time_change(_, new_time)
    last_remaining_time = new_time
end

function playback_finished(event)
    json = mputils.format_json({
        host=hostname,
        path=last_file_path,
        time=os.date('%c')
    })

    if last_remaining_time > minimum_remaining_time then
        mp.log('info', string.format(
            'Too much remaining time (%.02f > %.02f), skipping',
            last_remaining_time,
            minimum_remaining_time))
    else
        mp.log('info', 'Sending JSON: ' .. json)
        output = run({
            args={
                'ssh',
                remote_host,
                'echo',
                escape(json),
                '>>',
                escape(remote_log_path)},
            cancellable=false})
    end
end

----------

minimum_remaining_time = 120 --seconds
remote_host = 'burza'
remote_log_path = '/srv/www/tmp.sakuya.pl/public_html/mal/watched.lst'
hostname = run({args={'hostname'}, cancellable=false})

mp.observe_property('path', 'string', on_path_change)
mp.observe_property('time-remaining', 'native', on_time_change)
mp.register_event('end-file', playback_finished)
