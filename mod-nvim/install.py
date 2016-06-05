import packages
import util

spell_dir = '~/.config/nvim/spell/'
packages.try_install('neovim-git')
packages.try_install('fzf')

for dir in ['undo', 'backup', 'swap', 'spell']:
    util.create_dir('~/.config/nvim/' + dir)

for path in util.find('./*.vim'):
    util.create_symlink(path, '~/.config/nvim/')
util.create_symlink('./spell/pl.utf-8.add', spell_dir)
util.create_symlink('./spell/en.utf-8.add', spell_dir)
util.download('ftp://ftp.vim.org/pub/vim/runtime/spell/en.utf-8.spl', '~/.config/nvim/spell/')
util.download('ftp://ftp.vim.org/pub/vim/runtime/spell/pl.utf-8.spl', '~/.config/nvim/spell/')
util.download('https://raw.githubusercontent.com/junegunn/vim-plug/master/plug.vim', '~/.config/nvim/autoload/plug.vim')
util.create_file('~/.config/zsh/editor.sh', 'export EDITOR=nvim;alias vim=nvim', overwrite=True)

commands = ['PlugInstall']
for path in util.find(spell_dir):
    if 'add' in path and not 'spl' in path:
        commands.append('mkspell! ' + path)
util.run_verbose(['nvim'] + sum([['-c', cmd] for cmd in commands], []))
