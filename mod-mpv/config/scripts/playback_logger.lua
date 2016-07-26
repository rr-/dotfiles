mputils = require 'mp.utils'
require 'os'

-- configuration
minimum_watched_percentage = 80
minimum_duration = 300 -- five minutes
ignore_online_streams = true
remote_host = 'burza'
remote_log_path = '/srv/www/tmp.sakuya.pl/public_html/mal/watched.lst'
allowed_extensions = {'mpv', 'mp4', 'avi', 'm4v', 'mov', 'flv', 'mpeg', 'mpg', 'wmv', 'ogv', 'webm', 'rm'}

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

function table.contains(table, element)
    for _, value in pairs(table) do
        if value == element then
            return true
        end
    end
    return false
end

function get_file_extension(path)
    return path:match("^.+%.(.+)$")
end

function trim(path)
    return string.match(path, '^%s*(.-)%s*$')
end

function run(t)
    return trim(mputils.subprocess(t).stdout)
end

function playback_finished(event)
    path = mp.get_property('path')
    watched_percentage = mp.get_property_number('percent-pos')
    duration = mp.get_property_number('duration')
    hostname = run({args={'hostname'}, cancellable=false})
    extension = get_file_extension(path)

    if not table.contains(allowed_extensions, extension) then
        mp.log('warn', 'Extension doesn\'t match allowed files, skipping')
        return
    end

    if duration == null then
        mp.log('warn', 'No information on duration, skipping')
        return
    end

    if watched_percentage == null then
        mp.log('warn', 'No information on % watched, skipping')
        return
    end

    if ignore_online_streams and string.match(path, 'https?:') then
        mp.log('info', 'Online stream detected, skipping')
        return
    end

    if watched_percentage < minimum_watched_percentage then
        mp.log('info', string.format(
            'Watched too little (%.02f%% < %.02f%%), skipping',
            watched_percentage,
            minimum_watched_percentage))
        return
    end

    if duration < minimum_duration then
        mp.log('info', string.format(
            'File is too short (%.02fs < %.02fs), skipping',
            duration,
            minimum_duration))
        return
    end

    json = mputils.format_json({
        date=os.date('%c'),
        host=hostname,
        path=path
    })

    json = run({
        args={
            'sh',
            '-c',
            'echo ' .. escape(json) .. '|' ..
            'python -c "import json,sys;print(json.dumps(json.load(sys.stdin),sort_keys=True))"'},
        cancellable=false})

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

----------

mp.add_hook('on_unload', 50, playback_finished)
