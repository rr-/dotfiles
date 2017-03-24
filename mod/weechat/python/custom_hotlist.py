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


class HotlistItem:
    def __init__(self, number, priority, name, count):
        self.number = number
        self.priority = priority
        self.name = name
        self.count = count

    @property
    def title(self):
        ret = '%d:%s' % (self.number, self.name)
        if self.count:
            ret += '(%d)' % self.count
        return ret


def hotlist_item_cb(data, item, window):
    items = []

    hdata_hotlist = w.hdata_get('hotlist')
    ptr_hotlist = w.hdata_get_list(hdata_hotlist, 'gui_hotlist')
    while ptr_hotlist:
        priority = w.hdata_integer(hdata_hotlist, ptr_hotlist, 'priority')
        buffer = w.hdata_pointer(hdata_hotlist, ptr_hotlist, 'buffer')
        count = w.hdata_integer(
            hdata_hotlist, ptr_hotlist, '%d|count' % GUI_HOTLIST_MESSAGE)
        number = w.buffer_get_integer(buffer, 'number')
        name = w.buffer_get_string(buffer, 'short_name')

        items.append(HotlistItem(number, priority, name, count))
        ptr_hotlist = w.hdata_move(hdata_hotlist, ptr_hotlist, 1)

    return ' '.join(
        '%s %s %s' % (
            w.color(COLORS[item.priority]),
            item.title,
            w.color('reset'))
        for item in sorted(items, key=lambda item: (item.number, item.priority))
        if item.priority != GUI_HOTLIST_LOW)


def hotlist_hook_cb(data, signal, signal_data):
    w.bar_item_update('custom_hotlist')
    return w.WEECHAT_RC_OK


def my_signal_cb(data, signal, signal_data):
    return w.WEECHAT_RC_OK


if w.register(
        SCRIPT_NAME,
        SCRIPT_AUTHOR,
        SCRIPT_VERSION,
        SCRIPT_LICENSE,
        SCRIPT_DESC,
        '',
        ''):
    w.bar_item_new('custom_hotlist', 'hotlist_item_cb', '')
    w.hook_signal('buffer_line_added', 'hotlist_hook_cb', '')
