require 'mp.options'
local utils = require 'mp.utils'

local options = {
    visible = true,
    format = 'hello',
}
read_options(options, 'statusbar')

local osd = mp.create_osd_overlay("ass-events")

function round(number, decimals)
    local power = 10^decimals
    return math.floor(number * power) / power
end

function update_from_exif(exif)
    local file_info = table.concat({
        mp.get_property('width') .. ' × ' .. mp.get_property('height'),
        round((mp.get_property('file-size') or 0) / 1024 / 1024, 2) .. ' MB',
    }, ', ')

    local exposure_info = table.concat({
        exif['FocalLength'] and exif['FocalLength'],
        exif['ExposureTime'] and exif['ExposureTime'] .. ' s',
        exif['Aperture'] and 'f/' ..  exif['Aperture'],
        exif['ISO'] and 'ISO ' .. exif['ISO'],
    }, ', ')

    local model_info = table.concat({
        exif['Model'],
        exif['LensModel']
    }, ' + ')

    local rows = {
        string.find(file_info, '%S') and file_info,
        string.find(exposure_info, '%S') and exposure_info,
        string.find(model_info, '%S') and model_info,
    }

    osd.data = "{\\an1}" .. table.concat(rows, '\\N')
    osd:update()
end

function update()
    if options.visible == true then
        local path = mp.get_property('path')
        local reply = utils.subprocess({args={"exiftool", path, "-j"}})
        if reply.status == 0 then
            local exif = utils.parse_json(reply.stdout)[1]
            update_from_exif(exif)
            return
        end
    end

    osd.data = ""
    osd:update()
end

function on_file_load()
    update()
end

function on_toggle()
    options.visible = not options.visible
    update()
end


mp.register_event('file-loaded', on_file_load)
mp.register_script_message('toggle', on_toggle)
