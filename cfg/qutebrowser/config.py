palette = "dark"

c.auto_save.session = True
if palette == "dark":
    c.colors.tabs.even.bg = "#000"
    c.colors.tabs.odd.bg = "#000"
    c.colors.tabs.even.fg = "#FFF"
    c.colors.tabs.odd.fg = "#FFF"
    c.colors.tabs.selected.even.bg = "#015B82"
    c.colors.tabs.selected.even.fg = "#CDE"
    c.colors.tabs.selected.odd.bg = "#015B82"
    c.colors.tabs.selected.odd.fg = "#CDE"
else:
    c.colors.tabs.even.bg = "#EEE"
    c.colors.tabs.odd.bg = "#EEE"
    c.colors.tabs.even.fg = "#000"
    c.colors.tabs.odd.fg = "#000"
    c.colors.tabs.selected.even.bg = "#46AAFE"
    c.colors.tabs.selected.even.fg = "#000"
    c.colors.tabs.selected.odd.bg = "#46AAFE"
    c.colors.tabs.selected.odd.fg = "#000"

c.downloads.remove_finished = 10000
c.downloads.position = "bottom"
c.tabs.padding["top"] = 2
c.tabs.padding["bottom"] = 2
c.tabs.indicator.padding["top"] = 1
c.tabs.indicator.padding["bottom"] = 1
c.fonts.hints = "12px sans-serif"
c.fonts.tabs = "14px sans-serif"
c.fonts.monospace = "Input Mono"

c.editor.command = [
    "urxvt",
    "-e",
    "nvim",
    "-f",
    "{file}",
    "-c",
    "normal {line}G{column0}l",
]

c.hints.auto_follow_timeout = 300
c.hints.mode = "number"
c.tabs.title.format = "{index}: {title} {audio}"
c.downloads.location.directory = "~/"
c.completion.web_history.max_items = 1000

c.url.searchengines = {
    "DEFAULT": "https://google.com/search?hl=en&q={}",
    "startpage": "https://www.startpage.com/do/search?lui=english&language=english&cat=web&nj=0&query={}",
}

config.bind(
    ";m",
    'hint links spawn sh -c "LD_LIBRARY_PATH=/usr/local/lib mpv {hint-url}"',
)
config.bind(";t", "hint links spawn qbittorrent {hint-url}")
config.bind(";T", "hint -r links spawn qbittorrent {hint-url}")
config.bind("<", "navigate prev")
config.bind(">", "navigate next")
config.bind("<alt+9>", "tab-focus 9")
config.bind("J", "scroll-px 0 400")
config.bind("K", "scroll-px 0 -400")
config.bind("<space>", "scroll-page 0 1")
config.bind("gT", "tab-prev")
config.bind("gt", "tab-next")
config.bind("gn", "open -t about:blank")
config.bind("<ctrl-f11>", "set tabs.show never;; set statusbar.hide true")
config.bind("<shift-f11>", "set tabs.show always;; set statusbar.hide false")
