from libdotfiles.packages import try_install
from libdotfiles.util import HOME_DIR, create_file, get_distro_name

if get_distro_name() == "arch":
    try_install("chromium")

create_file(
    HOME_DIR / ".local" / "bin" / "browser",
    "#!/bin/sh\nchromium ${@}",
    overwrite=True,
)
(HOME_DIR / ".local" / "bin" / "browser").chmod(0o777)
