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
weechat.hook_print("", "notify_private", "", 1, "oscn_notify_private", "")


def notify(name, message):
    subprocess.check_output(
        [
            "/home/rr-/.local/bin/notify-urxvt",
            "weechat",
            "[%s] %s" % (name, message),
        ]
    )


def get_muted_highlight_nicks(buffer):
    result = []
    for item in weechat.buffer_get_string(
        buffer, "hotlist_max_level_nicks"
    ).split(","):
        try:
            nick, level = item.rsplit(":")
            level = int(level)
        except ValueError:
            continue
        if level < 3:
            result.append(nick.lower())
    return result


def oscn_irc_privmsg(
    data, buffer, date, tags, displayed, highlight, prefix, message
):
    name = weechat.buffer_get_string(
        buffer, "short_name"
    ) or weechat.buffer_get_string(buffer, "name")

    is_private = (
        weechat.buffer_get_string(buffer, "localvar_type") == "private"
    )

    notify_chat = weechat.config_get_plugin("notify_highlights") == "on"
    notify_privmsg = (
        weechat.config_get_plugin("notify_private_messages") == "on"
    )

    is_muted = (prefix or "").lower() in get_muted_highlight_nicks(buffer)

    if (
        displayed
        and not is_muted
        and (
            (is_private and notify_privmsg and prefix.lower() == name.lower())
            or (highlight and notify_chat)
        )
    ):
        notify(prefix, message)

    return weechat.WEECHAT_RC_OK


def oscn_notify_private(
    data, buffer, date, tags, displayed, highlight, prefix, message
):
    if "irc_privmsg" in tags:
        return weechat.WEECHAT_RC_OK

    notify_chat = weechat.config_get_plugin("notify_highlights") == "on"
    notify_privmsg = (
        weechat.config_get_plugin("notify_private_messages") == "on"
    )

    is_muted = (prefix or "").lstrip("&").lower() in get_muted_highlight_nicks(
        buffer
    )

    if displayed and not is_muted and notify_privmsg:
        notify(prefix, message)

    return weechat.WEECHAT_RC_OK
