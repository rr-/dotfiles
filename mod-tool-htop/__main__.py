import logs
import packages
import util

packages.try_install('htop')
util.create_symlink('#/htoprc', '~/.config/htop/htoprc')
