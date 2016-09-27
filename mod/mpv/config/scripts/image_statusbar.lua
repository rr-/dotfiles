local on = mp.get_opt('images-statusbar') == 'yes'

-- lua-filesize, generate a human readable string describing the file size
-- Copyright (c) 2016 Boris Nagaev
-- See the LICENSE file for terms of use.

local si = {"B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB"}

local function isNan(num)
    -- http://lua-users.org/wiki/InfAndNanComparisons
    -- NaN is the only value that doesn't equal itself
    return num ~= num
end

local function roundNumber(num, digits)
    local fmt = "%." .. digits .. "f"
    return tonumber(fmt:format(num))
end

local function get_file_size(size)
    if size == 0 then
        return "0" .. si[1]
    end
    local exponent = math.floor(math.log(size) / math.log(1024))
    if exponent > 8 then
        exponent = 8
    end
    local value = roundNumber(
        size / math.pow(2, exponent * 10), exponent > 0 and 1 or 0)
    local suffix = si[exponent + 1]
    return tostring(value):gsub('%.0$', '') .. suffix
end

function get_property_number_or_nil(name)
    if mp.get_property(name) == nil then
        return nil
    end
    return mp.get_property_number(name)
end

function update_statusbar()
    if on == true then
        local playlist_pos = mp.get_property_number('playlist-pos') + 1
        local playlist_count = mp.get_property_number('playlist-count')
        local width = get_property_number_or_nil('width')
        local height = get_property_number_or_nil('height')
        local size = get_file_size(mp.get_property_number('file-size'))
        local path = mp.get_property('filename')
        mp.set_property(
            'options/osd-msg1',
            string.format(
                '%s %sx%s %s (%d/%d)',
                path,
                width or '?',
                height or '?',
                size,
                playlist_pos,
                playlist_count))
        mp.set_property(
            'options/osd-msg3',
            string.format(
                '%s',
                path))
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
