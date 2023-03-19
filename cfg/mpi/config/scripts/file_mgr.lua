-- Helper for culling photos (raws + JPEGs).
-- Moves the currently viewed image and its associated raws to ../selected/{DIRNAME}/.

local mp_utils = require('mp.utils')


function string.starts(input, prefix)
   return string.sub(input, 1, string.len(prefix)) == prefix
end


local function dirname(pathname)
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


local function basename(pathname)
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


local function dir_create(target_path)
    mp.command_native({
        name = 'subprocess',
        playback_only = false,
        args = {'mkdir', '-p', target_path},
    })
end


local function file_copy(source_path, target_path)
    dir_create(dirname(target_path))
    mp.commandv('run', 'cp', source_path, target_path)
end


local function file_rename(source_path, target_path, keep_file_in_playlist)
    local old_pos = mp.get_property('playlist-pos')
    local current_path = mp.get_property('playlist/' .. tostring(old_pos) .. '/filename')
    if current_path == source_path then
        mp.commandv('playlist-remove', old_pos)
    end

    dir_create(dirname(target_path))
    mp.commandv('run', 'mv', source_path, target_path)

    if keep_file_in_playlist and current_path == source_path then
        mp.commandv('loadfile', target_path, 'append')
        local new_pos = mp.get_property('playlist-count') - 1
        mp.commandv('playlist-move', new_pos, old_pos)
        mp.set_property('playlist-pos', old_pos)
    end
end


local function select_file()
    local current_path = mp.get_property('path')
    local current_name = mp.get_property('filename')
    if current_name == nil then
        return
    end

    local current_name_no_ext = current_name:match('(.*)[.]')
    local current_dir = dirname(current_path)

    local files = mp_utils.readdir(current_dir, 'files')
    if files ~= nil then
        for _, file in pairs(files) do
            if string.starts(file, current_name_no_ext) then
                local source_name = file
                local source_path = mp_utils.join_path(current_dir, source_name)
                local source_name_no_ext = source_name:match('(.*)[.]')
                local source_name_ext = source_name:match('.*([.].*)')

                local target_name
                if string.find(source_name_no_ext, '-SELECTED') then
                    target_name = source_name_no_ext:gsub('-SELECTED', '') .. source_name_ext
                else
                    target_name = source_name_no_ext .. '-SELECTED' .. source_name_ext
                end
                local target_path = mp_utils.join_path(current_dir, target_name)

                mp.commandv('show-text', source_name .. ' renamed to ' .. target_name)
                file_rename(source_path, target_path, true)
            end
        end
    end
end


local function discard_file()
    local current_path = mp.get_property('path')
    local current_name = mp.get_property('filename')
    if current_name == nil then
        return
    end

    local current_name_no_ext = current_name:match('(.*)[.]')
    local current_dir = dirname(current_path)

    local files = mp_utils.readdir(current_dir, 'files')
    if files ~= nil then
        for _, file in pairs(files) do
            if string.starts(file, current_name_no_ext) then
                local source_name = file
                local source_path = mp_utils.join_path(current_dir, source_name)

                local target_name
                if string.find(source_name, '~') then
                    target_name = source_name:gsub('~', '')
                else
                    target_name = source_name .. '~'
                end
                local target_path = mp_utils.join_path(current_dir, target_name)

                mp.commandv('show-text', source_name .. ' renamed to ' .. target_name)
                file_rename(source_path, target_path, false)
            end
        end
    end
end


mp.register_script_message('select-file', select_file)
mp.register_script_message('discard-file', discard_file)
