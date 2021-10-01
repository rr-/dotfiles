from libdotfiles import HOME_DIR, PKG_DIR, packages, util

NVIM_DIR = HOME_DIR / ".config" / "nvim"
NVIM_SPELL_DIR = NVIM_DIR / "spell"

if util.distro_name() == "arch":
    packages.try_install("neovim")
    packages.try_install("pynvim", method="pip")
elif util.distro_name() == "linuxmint":
    packages.try_install("neovim")
    packages.try_install("python3-neovim")
packages.try_install("black", method="pip")
packages.try_install("isort", method="pip")

for dirname in ["undo", "backup", "swap", "spell"]:
    util.create_dir(NVIM_DIR / dirname)

util.create_symlinks(
    [(path, NVIM_DIR / path.name) for path in (PKG_DIR / "nvim").glob("*.vim")]
)

util.create_symlinks(
    [
        (path, NVIM_SPELL_DIR / path.name)
        for path in (PKG_DIR / "spell").glob("*.add")
    ]
)

util.create_symlink(PKG_DIR / "editorconfig", HOME_DIR / ".editorconfig")

util.download(
    "ftp://ftp.vim.org/pub/vim/runtime/spell/en.utf-8.spl",
    NVIM_SPELL_DIR / "en.utf-8.spl",
)
util.download(
    "ftp://ftp.vim.org/pub/vim/runtime/spell/pl.utf-8.spl",
    NVIM_SPELL_DIR / "pl.utf-8.spl",
)
util.download(
    "https://raw.githubusercontent.com/junegunn/vim-plug/master/plug.vim",
    NVIM_DIR / "autoload" / "plug.vim",
)
util.create_file(
    HOME_DIR / ".config" / "zsh" / "editor.sh",
    "export EDITOR=nvim;alias vim=nvim",
    overwrite=True,
)

commands = ["PlugInstall"]
for path in (NVIM_SPELL_DIR).glob("*.add"):
    commands.append("mkspell! " + str(path))
util.run_verbose(["nvim"] + sum([["-c", cmd] for cmd in commands], []))
