local mp_utils = require('mp.utils')

function run_vifm()
    local path = mp.get_property('path')
    local running = mp_utils.subprocess(
        {args = {'pidof', 'vifm'},
        cancellable=false,
    })['status'] == 0

    local args

    if running then
        args = {'vifm'}
        local extra_args = mp.get_opt('vifm-args')
        if extra_args ~= nil then
            for word in extra_args:gmatch('%S+') do
                mp.log('error', word)
                table.insert(args, word)
            end
        end
        table.insert(args, '--remote')
        table.insert(args, '--select')
        table.insert(args, path)
    else
        args = {'urxvt', '-e', 'vifm'}
    end

    mp_utils.subprocess_detached({args=args})
end

mp.register_script_message('run-vifm', run_vifm)
