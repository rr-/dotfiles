-- Helper for culling photos (raws + JPEGs).
-- Moves the currently viewed image and its associated raws to ../selected/{DIRNAME}/.

local mp_utils = require('mp.utils')

local last_removals = {}

function string.starts(input, prefix)
   return string.sub(input, 1, string.len(prefix)) == prefix
end


local function get_path_dirname(pathname)
    if pathname == nil then
        return '.'
    elseif type(pathname) ~= 'string' then
        error('pathname must be string', 2)
    end

    -- remove trailing-slashes
    local head = string.find(pathname, '/+$', 2)
    if head then
        pathname = string.sub(pathname, 1, head - 1)
    end

    -- remove last-segment
    head = string.find(pathname, '[^/]+$')
    if head then
        pathname = string.sub(pathname, 1, head - 1)
    end

    -- remove trailing-slashes
    head = string.find(pathname, '/+$')
    if head then
        if head == 1 then
            return '/'
        end
        pathname = string.sub(pathname, 1, head - 1)
    end

    -- empty or dotted string
    if string.find(pathname, '^%s*$') or string.find(pathname, '^%.+$') then
        return '.'
    end

    return pathname
end


local function get_path_basename(pathname)
    if pathname == nil then
        return '.'
    elseif type(pathname) ~= 'string' then
        error('pathname must be string', 2)
    end

    local head = string.find(pathname, '/+$', 2)
    if head then
        pathname = string.sub(pathname, 1, head - 1)
    end

    head = string.find(pathname, '[^/]+$')
    if head then
        pathname = string.sub(pathname, head)
    end

    if pathname == '' then
        return '.'
    end

    return pathname
end


local function playlist_get_pos()
    return mp.get_property_number('playlist-pos')
end


local function playlist_get_size()
    return mp.get_property_number('playlist-count')
end

local function playlist_set_pos(index)
    mp.set_property('playlist-pos', index)
end


local function playlist_pop_current()
    local old_pos = playlist_get_pos()
    mp.commandv('playlist-remove', old_pos)
end


local function playlist_insert(index, target_path)
    mp.commandv('loadfile', target_path, 'append')
    mp.commandv('playlist-move', playlist_get_size() - 1, index)
end


local function dir_create(target_path)
    mp.command_native({
        name = 'subprocess',
        playback_only = false,
        args = {'mkdir', '-p', target_path},
    })
end


local function file_copy(source_path, target_path)
    dir_create(get_path_dirname(target_path))
    mp.commandv('run', 'cp', source_path, target_path)
end


local function file_rename(source_path, target_path, keep_file_in_playlist)
    dir_create(get_path_dirname(target_path))
    mp.commandv('run', 'mv', source_path, target_path)

    mp.commandv('show-text', get_path_basename(source_path) .. ' renamed to ' .. get_path_basename(target_path))

    local playlist_pos = playlist_get_pos()
    local current_path = mp.get_property('path')
    if current_path == source_path then
        playlist_pop_current()
        if keep_file_in_playlist then
            playlist_insert(playlist_pos, target_path)
            playlist_set_pos(playlist_pos)
        end
    end
end


local function collect_file_group()
    local current_path = mp.get_property('path')
    local current_name = mp.get_property('filename')
    if current_name == nil then
        return {}
    end

    local current_name_no_ext = current_name:match('(.*)[.]')
    local current_dir = get_path_dirname(current_path)

    local files = mp_utils.readdir(current_dir, 'files')
    if files == nil then
        return {}
    end

    local result = {}
    for _, file in ipairs(files) do
        if string.starts(file, current_name_no_ext) then
            local source_path = mp_utils.join_path(current_dir, file)
            table.insert(result, source_path)
        end
    end
    return result
end


local function select_file()
    for _, source_path in ipairs(collect_file_group()) do
        local source_name = get_path_basename(source_path)
        local source_name_no_ext = source_name:match('(.*)[.]')
        local source_name_ext = source_name:match('.*([.].*)')

        local target_name
        if string.find(source_name_no_ext, '-SELECTED') then
            target_name = source_name_no_ext:gsub('-SELECTED', '') .. source_name_ext
        else
            target_name = source_name_no_ext .. '-SELECTED' .. source_name_ext
        end
        local target_path = mp_utils.join_path(get_path_dirname(source_path), target_name)

        file_rename(source_path, target_path, true)
    end
end


local function discard_file()
    local old_pos = playlist_get_pos()
    local current_path = mp.get_property('path')
    local removals = {}

    for _, source_path in ipairs(collect_file_group()) do
        local target_path = source_path .. '~'
        file_rename(source_path, target_path, false)
        table.insert(removals, {source_path, target_path})
    end

    table.insert(
        last_removals,
        {
            old_pos = old_pos,
            current_path = current_path,
            removals = removals,
        }
    )
end


local function undo_discard_file()
    if #last_removals < 1 then
        mp.commandv('show-text', 'Nothing to undo')
        return
    end

    local last_removal = table.remove(last_removals)
    for _, removal in ipairs(last_removal.removals) do
        local source_path = removal[1]
        local target_path = removal[2]
        file_rename(target_path, source_path, false)
    end

    playlist_insert(last_removal.old_pos, last_removal.current_path)
    playlist_set_pos(last_removal.old_pos)
end


mp.register_script_message('select-file', select_file)
mp.register_script_message('discard-file', discard_file)
mp.register_script_message('undo-discard-file', undo_discard_file)
