'''
Usage: put [custom_hotlist] in your status bar items.
'/set weechat.bar.status.items'.
'''

import weechat as w

SCRIPT_NAME = 'custom_hotlist'
SCRIPT_AUTHOR = 'rr- <rr-@sakuya.pl>'
SCRIPT_VERSION = '0.1'
SCRIPT_LICENSE = 'MIT'
SCRIPT_DESC = 'Bar item with custom hotlist'

GUI_HOTLIST_LOW = 0
GUI_HOTLIST_MESSAGE = 1
GUI_HOTLIST_PRIVATE = 2
GUI_HOTLIST_HIGHLIGHT = 3

COLORS = {
    0: '240,254',
    1: '240,252',
    2: '255,166',
    3: '255,166',
}

settings = {
}

def hotlist_item_cb(data, item, window):
    priorities = {}
    titles = {}

    #hdata_buffer = w.hdata_get('buffer')
    #ptr_buffer = w.hdata_get_list(hdata_buffer, 'gui_buffers')
    #while ptr_buffer:
    #    number = w.buffer_get_integer(ptr_buffer, 'number')
    #    priorities[number] = -1
    #    ptr_buffer = w.hdata_move(hdata_buffer, ptr_buffer, 1)

    hdata_hotlist = w.hdata_get('hotlist')
    ptr_hotlist = w.hdata_get_list(hdata_hotlist, 'gui_hotlist')
    while ptr_hotlist:
        priority = w.hdata_integer(hdata_hotlist, ptr_hotlist, 'priority')
        buffer = w.hdata_pointer(hdata_hotlist, ptr_hotlist, 'buffer')
        count = w.hdata_integer(
            hdata_hotlist, ptr_hotlist, '%d|count' % GUI_HOTLIST_MESSAGE)
        number = w.buffer_get_integer(buffer, 'number')
        name = w.buffer_get_string(buffer, 'short_name')

        if priority != GUI_HOTLIST_LOW:
            priorities[number] = priority
            titles[number] = '%d:%s' % (number, name)
            if count:
                titles[number] += '(%d)' % count

        ptr_hotlist = w.hdata_move(hdata_hotlist, ptr_hotlist, 1)

    result = ''
    for number, priority in sorted(priorities.items()):
        result += w.color(COLORS[priority]) + ' %s ' % titles[number]
    result += w.color('reset')
    return result

def hotlist_hook_cb(data, signal, signal_data):
    w.bar_item_update('custom_hotlist')
    return w.WEECHAT_RC_OK

def my_signal_cb(data, signal, signal_data):
    return weechat.WEECHAT_RC_OK

if w.register(SCRIPT_NAME, SCRIPT_AUTHOR, SCRIPT_VERSION, SCRIPT_LICENSE, SCRIPT_DESC, '', ''):
    for option, default_value in settings.iteritems():
        if not w.config_is_set_plugin(option):
            w.config_set_plugin(option, default_value)

    w.bar_item_new('custom_hotlist', 'hotlist_item_cb', '')
    hook = w.hook_signal('buffer_line_added', 'hotlist_hook_cb', '')
