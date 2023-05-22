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
    local width = mp.get_property('width')
    local height = mp.get_property('height')
    local filesize = mp.get_property('file-size') or 0

    local model = exif['Model']
    local lens = exif['LensModel']
    if model and lens then
        model_lens = model .. ' + ' .. lens
    elseif model then
        model_lens = model
    elseif lens then
        model_lens = lens
    end

    osd.data = (
        "{\\an1}"
        .. width .. ' × ' .. height .. ', '
        .. round(filesize / 1024 / 1024, 2) .. ' MB\\N'
        .. exif['FocalLength'] .. ', '
        .. exif['ExposureTime'] .. ' s, '
        .. 'f/' .. exif['Aperture'] .. ', '
        .. 'ISO ' .. exif['ISO'] .. '\\N'
        .. model_lens
    )
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
