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

These are personal Linux configurations, primarily for Arch Linux, with
Ubuntu and Linux Mint branches in some installers. Package names and
availability vary by distribution; inspect the module's `cfg/<name>/__main__.py`
before running it on a new machine.

The shared installer requires Python 3.13 or newer. Run it from the repository
root. No Poetry environment or Python dependency installation is needed for
the shared helpers; `coloredlogs` is optional. Some modules have additional
Python or system dependencies. Scripts whose first line uses `uv run` require
[uv](https://docs.astral.sh/uv/) and declare their Python dependencies inline.
The Rust tools require Cargo and a Rust compiler supporting edition 2024;
`cull` also needs SDL3 development files and FFmpeg.

Every module can be installed with `./install` like this:

```console
./install zsh
./install nvim
./install wezterm
```

Most things are installed using symbolic links.

The installation scripts also try to install relevant packages using various
package managers, e.g. `./install zsh` will try downloading `zsh` with a
package manager relevant to the current Linux distribution.

Package installation is best effort: errors are logged and configuration
continues, since a package may have a different name on your distribution or
already be installed outside its package manager. Check the output and
install missing dependencies manually. System package installation may invoke
`sudo`; pip installs use `--user --break-system-packages`.

Existing ordinary files at symlink destinations are protected: move or back
them up yourself before retrying. Existing symlinks may be replaced. Some
modules also write files or change system settings, so review the module
before running it. There is no general rollback or uninstall command.

Failed downloads leave the destination untouched and can be retried by
rerunning the module. Empty or partial files left by older installer versions
must be moved aside manually first. A pre-existing Git checkout must point
to the expected origin; a mismatch stops that module.

### Development checks

Create a virtual environment and install the development tools:

```console
python3 -m venv .venv
.venv/bin/python -m pip install '.[dev]'
```

With that environment activated, run:

```console
ruff format --check .
ruff check .
ty check libdotfiles tests bin/util/aes-edit
python -m unittest discover -s tests -v
cargo test --locked --manifest-path opt/trash/Cargo.toml
cargo test --locked --manifest-path opt/cull/Cargo.toml
```

CI runs these checks. Python regression tests use temporary directories and
mock package-manager and network operations; they do not install system
packages or modify your home configuration. The Rust tests run without a GUI.
