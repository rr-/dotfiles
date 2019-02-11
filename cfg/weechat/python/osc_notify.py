import string
import subprocess
import sys

import weechat

weechat.register(
    "osc_notify",
    "ulhume",
    "0.1.3",
    "GPL3",
    "osc_notify - Terminal OSC notification",
    "",
    "",
)

settings = {"notify_highlights": "on", "notify_private_messages": "on"}

for option, default_value in settings.items():
    if weechat.config_get_plugin(option) == "":
        weechat.config_set_plugin(option, default_value)

weechat.hook_print("", "irc_privmsg", "", 1, "oscn_irc_privmsg", "")


def notify(name, message):
    subprocess.check_output(
        [
            "/home/rr-/.local/bin/notify-urxvt",
            "weechat",
            "[%s] %s" % (name, message),
        ]
    )


def oscn_irc_privmsg(
    data, buffer, date, tags, displayed, highlight, prefix, message
):
    name = weechat.buffer_get_string(
        buffer, "short_name"
    ) or weechat.buffer_get_string(buffer, "name")

    if (
        weechat.buffer_get_string(buffer, "localvar_type") == "private"
        and weechat.config_get_plugin("notify_private_messages") == "on"
        and name == prefix
    ) or (
        highlight == "1"
        and weechat.config_get_plugin("notify_highlights") == "on"
    ):
        notify(name, message)

    return weechat.WEECHAT_RC_OK
