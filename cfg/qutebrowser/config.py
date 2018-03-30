c.auto_save.session = True
c.colors.tabs.even.bg = 'black'
c.colors.tabs.odd.bg = 'black'
c.colors.tabs.selected.even.bg = '#015B82'
c.colors.tabs.selected.even.fg = '#CDE'
c.colors.tabs.selected.odd.bg = '#015B82'
c.colors.tabs.selected.odd.fg = '#CDE'
c.downloads.remove_finished = 10000
c.downloads.position = 'bottom'
c.fonts.hints = 'bold 12px monospace'
c.fonts.monospace = 'Input Mono'
c.hints.auto_follow_timeout = 300
c.hints.mode = 'number'

c.url.searchengines = {
    'DEFAULT': 'https://google.com/search?hl=en&q={}',
    'startpage': 'https://www.startpage.com/do/search?lui=english&language=english&cat=web&nj=0&query={}',
}

config.bind(';m', 'hint links spawn sh -c "LD_LIBRARY_PATH=/usr/local/lib mpv {hint-url}"')
config.bind('<', 'navigate prev')
config.bind('>', 'navigate next')
config.bind('<alt+9>', 'tab-focus 9')
config.bind('J', 'scroll-px 0 400')
config.bind('K', 'scroll-px 0 -400')
config.bind('<space>', 'scroll-page 0 1')
config.bind('gT', 'tab-prev')
config.bind('gt', 'tab-next')
config.bind('gn', 'open -t about:blank')
