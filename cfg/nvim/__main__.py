from libdotfiles.packages import try_install
from libdotfiles.util import (
    HOME_DIR,
    PKG_DIR,
    create_dir,
    create_file,
    create_symlink,
    create_symlinks,
    download_file,
    run,
)

NVIM_DIR = HOME_DIR / ".config" / "nvim"
NVIM_SPELL_DIR = NVIM_DIR / "spell"

try_install("neovim")

for dirname in ["undo", "backup", "swap", "spell"]:
    create_dir(NVIM_DIR / dirname)

create_symlinks(
    [(path, NVIM_DIR / path.name) for path in (PKG_DIR / "nvim").glob("*")]
)

create_symlinks(
    [
        (path, NVIM_SPELL_DIR / path.name)
        for path in (PKG_DIR / "spell").glob("*.add")
    ]
)

create_symlink(PKG_DIR / "editorconfig", HOME_DIR / ".editorconfig")

download_file(
    "ftp://ftp.vim.org/pub/vim/runtime/spell/en.utf-8.spl",
    NVIM_SPELL_DIR / "en.utf-8.spl",
)
download_file(
    "ftp://ftp.vim.org/pub/vim/runtime/spell/pl.utf-8.spl",
    NVIM_SPELL_DIR / "pl.utf-8.spl",
)
create_file(
    HOME_DIR / ".config" / "zsh" / "editor.sh",
    "export EDITOR=nvim;alias vim=nvim",
    overwrite=True,
)

commands = ["mkspell! " + str(path) for path in NVIM_SPELL_DIR.glob("*.add")]
if commands:
    run(
        ["nvim", "--headless"]
        + sum([["-c", cmd] for cmd in commands], [])
        + ["-c", "qa"],
        check=False,
    )
