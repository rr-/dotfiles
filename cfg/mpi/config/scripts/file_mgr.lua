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


local function select_file()
    local source_path = mp.get_property('path')
    local source_name = mp.get_property('filename')
    if source_name == nil then
        return
    end

    local source_name_no_ext = source_name:match('(.*)[.]')
    local source_dir = dirname(source_path)
    local source_dir_name = basename(source_dir)

    local target_dir = source_dir
    target_dir = mp_utils.join_path(target_dir, '..')
    target_dir = mp_utils.join_path(target_dir, 'selected')
    target_dir = mp_utils.join_path(target_dir,source_dir_name)

    mp.command_native({
        name = 'subprocess',
        playback_only = false,
        args = {'mkdir', '-p', target_dir},
    })

    local files = mp_utils.readdir(source_dir, 'files')
    if files ~= nil then
        for _, file in pairs(files) do
            if string.starts(file, source_name_no_ext) then
                local file_path = mp_utils.join_path(source_dir, file)
                mp.commandv('run', 'cp', file_path, target_dir)
                mp.commandv('show-text', file .. ' copied to ' .. target_dir)
            end
        end
    end
end


mp.register_script_message('select-file', select_file)
