from dotinstall import packages, util


def run():
    spell_dir = "~/.config/vim/spell/"

    choices = [
        "vim",
        "gvim",  # gvim supports for X11 clipboard, but has more dependencies
    ]
    choice = None
    while choice not in choices:
        choice = input("Which package to install? (%s) " % choices).lower()
    packages.try_install(choice)
    packages.try_install("fzf")

    for name in ["undo", "backup", "swap", "spell", "autoload"]:
        util.create_dir("~/.config/vim/" + name)

    for path in util.find("./../nvim/*.vim"):
        util.create_symlink(path, "~/.config/vim/")
    util.create_symlink("./../nvim/spell/pl.utf-8.add", spell_dir)
    util.create_symlink("./../nvim/spell/en.utf-8.add", spell_dir)
    util.download(
        "ftp://ftp.vim.org/pub/vim/runtime/spell/en.utf-8.spl",
        "~/.config/vim/spell/",
    )
    util.download(
        "ftp://ftp.vim.org/pub/vim/runtime/spell/pl.utf-8.spl",
        "~/.config/vim/spell/",
    )
    util.download(
        "https://raw.githubusercontent.com/junegunn/vim-plug/master/plug.vim",
        "~/.config/vim/autoload/plug.vim",
    )
    util.create_file(
        "~/.config/zsh/editor.sh", "export EDITOR=vim", overwrite=True
    )
    util.create_symlink("~/.config/vim/", "~/.vim")
    util.create_symlink("~/.config/vim/init.vim", "~/.vimrc")

    commands = ["PlugInstall"]
    for path in util.find(spell_dir):
        if "add" in path and "spl" not in path:
            commands.append("mkspell! " + path)
    util.run_verbose(["vim"] + sum([["-c", cmd] for cmd in commands], []))
