from libdotfiles.packages import try_install
from libdotfiles.util import HOME_DIR, create_file, get_distro_name

if get_distro_name() == "arch":
    try_install("brave-bin")

create_file(
    HOME_DIR / ".local" / "bin" / "browser",
    "#!/bin/sh\nbrave ${@}",
    overwrite=True,
)
(HOME_DIR / ".local" / "bin" / "browser").chmod(0o777)

# the theme switcher renders into here; brave loads it as an unpacked
# extension, which needs the directory to exist before the first switch
(HOME_DIR / ".config" / "theme.d" / "brave-theme").mkdir(
    parents=True, exist_ok=True
)
