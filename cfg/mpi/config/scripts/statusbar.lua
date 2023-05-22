require 'mp.options'

local options = {
    visible = true,
    format = 'hello',
}
read_options(options, 'statusbar')

local osd = mp.create_osd_overlay("ass-events")

function update()
    local message = mp.command_native({"expand-text", options.format})
    if options.visible == true then
        osd.data = "{\\an3}" .. message
    else
        osd.data = ""
    end
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
