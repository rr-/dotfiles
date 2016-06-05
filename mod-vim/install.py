import packages
import util

spell_dir = '~/.config/vim/spell/'

choices = ['vim', 'gvim'] # gvim supports for X11 clipboard, but has more dependencies
choice = None
while choice not in choices:
    choice = input('Which package to install? (%s) ' % choices).lower()
packages.try_install(choice)
packages.try_install('fzf')

for dir in ['undo', 'backup', 'swap', 'spell', 'autoload']:
    util.create_dir('~/.config/vim/' + dir)

for path in util.find('./../mod-nvim/*.vim'):
    util.create_symlink(path, '~/.config/vim/')
util.create_symlink('./../mod-nvim/spell/pl.utf-8.add', spell_dir)
util.create_symlink('./../mod-nvim/spell/en.utf-8.add', spell_dir)
util.download('ftp://ftp.vim.org/pub/vim/runtime/spell/en.utf-8.spl', '~/.config/vim/spell/')
util.download('ftp://ftp.vim.org/pub/vim/runtime/spell/pl.utf-8.spl', '~/.config/vim/spell/')
util.download('https://raw.githubusercontent.com/junegunn/vim-plug/master/plug.vim', '~/.config/vim/autoload/plug.vim')
util.create_file('~/.config/zsh/editor.sh', 'export EDITOR=vim', overwrite=True)
util.create_symlink('~/.config/vim/', '~/.vim')
util.create_symlink('~/.config/vim/init.vim', '~/.vimrc')

commands = ['PlugInstall']
for path in util.find(spell_dir):
    if 'add' in path and not 'spl' in path:
        commands.append('mkspell! ' + path)
util.run_verbose(['vim'] + sum([['-c', cmd] for cmd in commands], []))
