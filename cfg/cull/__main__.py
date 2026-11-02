from libdotfiles.packages import try_install
from libdotfiles.util import HOME_DIR, REPO_ROOT_DIR, create_symlink, run

try_install("ffmpeg")
try_install("sdl3")

project_dir = REPO_ROOT_DIR / "opt" / "cull"
run(
    [
        "cargo",
        "build",
        "--release",
        "--manifest-path",
        project_dir / "Cargo.toml",
    ],
    check=True,
)

create_symlink(
    project_dir / "target" / "release" / "cull",
    HOME_DIR / ".local" / "bin" / "cull",
)
