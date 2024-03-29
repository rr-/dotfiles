dotfiles
--------

This repository contains configuration files and scripts tailored to my needs
or preferences. Some of these might prove useful to other people. The most
custom goodies are located in the `bin/` directory.

#### Repository structure

- `bin/`: custom tools
- `cfg/`: configuration and installers for third party programs
- `libdotfiles/`: code that powers the installers
- `opt/`: projects too big to fit in `bin/`

### Installing a module

Every module can be installed with `./install` like this:

```console
./install zsh
./install vim
./install urxvt
```

Most things are installed using symbolic links.

The installation scripts also try to install relevant packages using various
package managers, e.g. `./install zsh` will try downloading `zsh` with a
package manager relevant to the current Linux distribution.
