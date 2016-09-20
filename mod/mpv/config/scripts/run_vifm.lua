local mp_utils = require('mp.utils')

function run_vifm()
    local path = mp.get_property('path')
    local running = mp_utils.subprocess(
        {args = {'pidof', 'vifm'},
        cancellable=false,
    })['status'] == 0

    local args
    if running then
        args = {'vifm', '--remote', '--select', path}
    else
        args = {'urxvt', '-e', 'vifm'}
    end
    mp_utils.subprocess_detached({args=args})
end

mp.register_script_message('run-vifm', run_vifm)
