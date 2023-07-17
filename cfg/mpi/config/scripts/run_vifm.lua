local last_known_path = nil
local mp_utils = require('mp.utils')

function string:split( inSplitPattern, outResults )
  if not outResults then
    outResults = { }
  end
  local theStart = 1
  local theSplitStart, theSplitEnd = string.find( self, inSplitPattern, theStart )
  while theSplitStart do
    table.insert( outResults, string.sub( self, theStart, theSplitStart-1 ) )
    theStart = theSplitEnd + 1
    theSplitStart, theSplitEnd = string.find( self, inSplitPattern, theStart )
  end
  table.insert( outResults, string.sub( self, theStart ) )
  return outResults
end

function playback_started()
    last_known_path = mp.get_property('path')
end

function is_vifm_running()
    return mp_utils.subprocess({
        args = {'pidof', 'vifm'},
        cancellable = false,
    })['status'] == 0
end

function get_vifm_server_name()
    return os.getenv('VIFM_SERVER_NAME')
end

function get_vifm_info(callback)
    local vifm_server_name = get_vifm_server_name()

    local args = {'vifm'}
    if vifm_server_name then
        table.insert(args, '--server-name')
        table.insert(args, vifm_server_name)
    end
    table.insert(args, '--remote-expr')
    table.insert(args, 'paneisat("left").expand("\\n%c\\n%C\\n%d\\n%D")')
    local result = mp_utils.subprocess({args = args, cancellable = false})
    local lines = result.stdout:gsub('\\', ''):split('\n')
    return {
        selected_pane = tonumber(lines[1]),
        current_file = lines[2],
        other_file = lines[3],
        current_dir = lines[4],
        other_dir = lines[5],
    }
end

function run_vifm()
    if not is_vifm_running() then
        mp_utils.subprocess_detached({args = {'urxvt', '-e', 'vifm'}})
        mp.command('quit')
    end

    local vifm_server_name = get_vifm_server_name()
    local vifm_info = get_vifm_info()
    local args = {'vifm'}
    if vifm_server_name then
        table.insert(args, '--server-name')
        table.insert(args, vifm_server_name)
    end
    table.insert(args, '--remote')
    if vifm_info.selected_pane == 1 then
        table.insert(args, '--select')
        table.insert(args, last_known_path)
    else
        table.insert(args, vifm_info.other_dir)
        table.insert(args, '--select')
        table.insert(args, last_known_path)
    end
    mp_utils.subprocess_detached({args = args})
    mp.command('quit')
end

mp.register_script_message('run-vifm', run_vifm)
mp.add_hook('on_load', 50, playback_started)
