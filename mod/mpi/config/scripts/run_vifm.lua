local mp_utils = require('mp.utils')
local last_known_path = nil

function playback_started(event)
    last_known_path = mp.get_property('path')
end

function run_vifm()
    local running = mp_utils.subprocess({
        args = {'pidof', 'vifm'},
        cancellable=false,
    })['status'] == 0

    local args

    if running then
        args = {'vifm'}
        vifm_server_name = os.getenv('VIFM_SERVER_NAME')
        if vifm_server_name then
            table.insert(args, '--server-name')
            table.insert(args, vifm_server_name)
        end
        table.insert(args, '--remote')
        table.insert(args, '--select')
        table.insert(args, last_known_path)
    else
        args = {'urxvt', '-e', 'vifm'}
    end

    mp_utils.subprocess_detached({args=args})
end

mp.register_script_message('run-vifm', run_vifm)
mp.add_hook('on_load', 50, playback_started)
