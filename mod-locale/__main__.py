import logs
import util

util.create_symlink('#/locale.conf', '~/.config/')
util.run_verbose(['sudo', 'sh', '-c', 'sed -i "s/#en_US.UTF-8/en_US.UTF-8/" /etc/locale.gen'])
util.run_verbose(['sudo', 'sh', '-c', 'sed -i "s/#pl_PL.UTF-8/pl_PL.UTF-8/" /etc/locale.gen'])
util.run_verbose(['sudo', 'sh', '-c', 'sed -i "s/#ja_JP.UTF-8/ja_JP.UTF-8/" /etc/locale.gen'])
util.run_verbose(['sudo', 'locale-gen'])
