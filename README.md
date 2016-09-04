dotfiles
--------

This repository contains configuration files and scripts tailored to my needs
or preferences. Some of these might prove useful to other people. The most
custom goodies are located in the `bin/` directory.

[![Screenshot](screen.png)](https://raw.githubusercontent.com/rr-/dotfiles/master/screen.png)
*What it roughly looks like when I'm not using a web browser*

#### Repository structure

- `bin/`: custom tools
- `mod/`: configuration and installers for third party programs
- `lib/`: code shared between scripts in `bin/` and modules in `mod/`
- `aux/`: miscellaneous executables
- `txt/`: miscellaneous text resources

### Installing module

All of modules can be installed with `./install` like this:

```console
./install zsh
./install vim
./install term.urxvt
```

Most things are installed using symbolic links.

The installation scripts also try to install relevant packages using various
package managers, e.g. `zsh` will try downloading only `zsh`, while `bspwm`
will download `bspwm-git`, `PyQt4` and other dependencies required for the full
`bspwm` setup.

#### Caveats

On fresh systems things such as `apt-cyg` and `yaourt` are missing and it's
tedious to install them by hand. For this reason, I've put them in separate
directory, `aux/`. These might get changed into `mod-tool-X` in the future.

Some modules will work only on GNU/Linux, but essential ones such as `vim` or
`zsh` will also work on Cygwin.

While the repository tries to be modular, some things (the ones having to do
with graphical environment) may not work. For example, I haven't tested panel
behavior if there is no mpd installed. Similarly, most AutoHotkey stuff makes
sense only if one has installed Cygwin and Firefox.
