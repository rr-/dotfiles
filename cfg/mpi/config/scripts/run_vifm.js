var last_known_path = null;

function playback_started(event) {
    last_known_path = mp.get_property('path');
}

function is_vifm_running() {
    return mp.utils.subprocess({
        args: ['pidof', 'vifm'],
        cancellable: false,
    })['status'] == 0;
}

function get_vifm_server_name() {
    return mp.utils.getenv('VIFM_SERVER_NAME');
}

// TODO: https://github.com/vifm/vifm/issues/293
function get_vifm_info(callback) {
    var vifm_server_name = get_vifm_server_name();
    var tmp_file = '/tmp/tmp.txt';

    args = ['vifm'];
    if (vifm_server_name) {
        args.push('--server-name');
        args.push(vifm_server_name);
    }
    args = args.concat([
        '--remote',
        '-c', 'execute "!echo " paneisat("left") ">' + tmp_file + '"',
        '-c', '!echo %c >>' + tmp_file,
        '-c', '!echo %C >>' + tmp_file,
        '-c', '!echo %d >>' + tmp_file,
        '-c', '!echo %D >>' + tmp_file,
    ]);
    var result = mp.utils.subprocess({args: args, cancellable: false});

    setTimeout(function() {
        var lines = mp.utils.read_file(tmp_file).split(/\n/);
        var info = {
            selected_pane: parseInt(lines[0]),
            current_file: lines[1],
            other_file: lines[2],
            current_dir: lines[3],
            other_dir: lines[4],
        };
        callback(info);
    }, 100);
}

function run_vifm() {
    if (!is_vifm_running()) {
        mp.utils.subprocess_detached({args: ['urxvt', '-e', 'vifm']});
        mp.command('quit');
    }

    var vifm_server_name = get_vifm_server_name();
    get_vifm_info(function(vifm_info) {
        var args = ['vifm'];
        if (vifm_server_name) {
            args.push('--server-name');
            args.push(vifm_server_name);
        }
        args.push('--remote');
        if (vifm_info.selected_pane === 1) {
            args.push('--select');
            args.push(last_known_path);
        } else {
            args.push(vifm_info.other_dir);
            args.push('--select');
            args.push(last_known_path);
        }
        mp.utils.subprocess_detached({args: args});
        mp.command('quit');
    });
}

mp.register_script_message('run-vifm', run_vifm);
mp.add_hook('on_load', 50, playback_started);