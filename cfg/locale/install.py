from libdotfiles import util


def run():
    util.create_symlink("./locale.conf", "~/.config/")
    for lang in ["en_US", "pl_PL", "ja_JP"]:
        util.run_verbose(
            [
                "sudo",
                "sh",
                "-c",
                'sed -i "s/#%s.UTF-8/%s.UTF-8/" /etc/locale.gen'
                % (lang, lang),
            ]
        )
    util.run_verbose(["sudo", "locale-gen"])
