from libdotfiles import HOME_DIR, PKG_DIR, util

util.create_symlink(
    PKG_DIR / "locale.conf", HOME_DIR / ".config" / "locale.conf"
)
for lang in ["en_US", "pl_PL", "ja_JP"]:
    util.run_verbose(
        [
            "sudo",
            "sh",
            "-c",
            'sed -i "s/#%s.UTF-8/%s.UTF-8/" /etc/locale.gen' % (lang, lang),
        ]
    )
util.run_verbose(["sudo", "locale-gen"])
