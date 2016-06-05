import packages
import util

packages.try_install('xorg')          # the server itself
packages.try_install('xclip')         # for clip to work
packages.try_install('xorg-xinit')    # for startx
packages.try_install('xorg-xsetroot') # to fix the mouse cursor
packages.try_install('xorg-xrandr')   # to query monitor information
packages.try_install('xdotool')       # for all sort of things
packages.try_install('autocutsel')    # synchronize primary and selection clipboards
packages.try_install('clipit')        # keep clipboard content even after application closes
packages.try_install('pkg-config')    # for compton
packages.try_install('compton')       # for shadows, transparency and vsync
packages.try_install('shot-git')      # for screenshots

util.create_symlink('./xinitrc', '~/.xinitrc')
util.create_symlink('./compton.conf', '~/.config/compton.conf')

if util.has_executable('zsh'):
    util.create_symlink('./zlogin', '~/.zlogin')
