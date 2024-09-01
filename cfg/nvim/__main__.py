from libdotfiles.packages import try_install
from libdotfiles.util import (
    HOME_DIR,
    PKG_DIR,
    create_dir,
    create_file,
    create_symlink,
    create_symlinks,
    download_file,
    get_distro_name,
    run,
)

NVIM_DIR = HOME_DIR / ".config" / "nvim"
NVIM_SPELL_DIR = NVIM_DIR / "spell"

if get_distro_name() == "arch":
    try_install("neovim")
    try_install("pynvim", method="pip")
elif get_distro_name() == "linuxmint":
    try_install("neovim")
    try_install("python3-neovim")
elif get_distro_name() == "ubuntu":
    try_install("neovim")
    try_install("pynvim", method="pip")
try_install("black", method="pip")
try_install("isort", method="pip")

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
download_file(
    "https://raw.githubusercontent.com/junegunn/vim-plug/master/plug.vim",
    NVIM_DIR / "autoload" / "plug.vim",
)
create_file(
    HOME_DIR / ".config" / "zsh" / "editor.sh",
    "export EDITOR=nvim;alias vim=nvim",
    overwrite=True,
)

commands = ["PlugInstall"]
for path in (NVIM_SPELL_DIR).glob("*.add"):
    commands.append("mkspell! " + str(path))
run(["nvim"] + sum([["-c", cmd] for cmd in commands], []), check=False)
