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
    local file_items = {}
    do
        local width = mp.get_property('width')
        local height = mp.get_property('height')
        local filesize = mp.get_property('file-size') or 0
        table.insert(file_items, width .. ' × ' .. height)
        table.insert(file_items, round(filesize / 1024 / 1024, 2) .. ' MB')
    end
    local file_info = table.concat(file_items, ', ')

    local model_items = {}
    do
        if exif['Model'] then
            table.insert(model_items, exif['Model'])
        end
        if exif['LensModel'] then
            table.insert(model_items, exif['LensModel'])
        end
    end
    local model_info = table.concat(model_items, ' + ')

    local exposure_items = {}
    do
        if exif['FocalLength'] then
            table.insert(exposure_items, exif['FocalLength'])
        end
        if exif['ExposureTime'] then
            table.insert(exposure_items, exif['ExposureTime'] .. ' s')
        end
        if exif['Aperture'] then
            table.insert(exposure_items, 'f/' ..  exif['Aperture'])
        end
        if exif['ISO'] then
            table.insert(exposure_items, 'ISO ' .. exif['ISO'])
        end
    end
    local exposure_info = table.concat(exposure_items, ', ')

    local rows = {}
    do
        if file_info and string.find(file_info, '%S') then
            table.insert(rows, file_info)
        end
        if exposure_info and string.find(exposure_info, '%S') then
            table.insert(rows, exposure_info)
        end
        if model_info and string.find(model_info, '%S') then
            table.insert(rows, model_info)
        end
    end

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
