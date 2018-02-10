local on = mp.get_opt('images-statusbar') == 'yes'
local msg1 = mp.get_property('options/osd-msg1')

function update_statusbar()
    if on == true then
        mp.set_property('options/osd-msg1', msg1)
    else
        mp.set_property('options/osd-msg1', '')
    end
end

function toggle_statusbar()
    on = not on
    update_statusbar()
    mp.osd_message('', 0)
end

mp.register_event('file-loaded', update_statusbar)
mp.register_script_message('toggle-statusbar', toggle_statusbar)
