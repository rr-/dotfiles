from libdotfiles.util import HOME_DIR, PKG_DIR, create_symlink, run

create_symlink(PKG_DIR / "locale.conf", HOME_DIR / ".config" / "locale.conf")
for lang in ["en_US", "pl_PL", "ja_JP"]:
    run(
        [
            "sudo",
            "sh",
            "-c",
            'sed -i "s/#%s.UTF-8/%s.UTF-8/" /etc/locale.gen' % (lang, lang),
        ],
        check=False,
    )
run(["sudo", "locale-gen"], check=False)
