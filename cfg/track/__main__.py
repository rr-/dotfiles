from libdotfiles.util import (
    HOME_DIR,
    REPO_ROOT_DIR,
    create_dir,
    create_symlink,
)

TRACK_DIR = REPO_ROOT_DIR / "opt" / "track"

create_dir(HOME_DIR / ".claude" / "skills")
create_dir(HOME_DIR / ".claude" / "hooks")
create_symlink(TRACK_DIR / "skill", HOME_DIR / ".claude" / "skills" / "track")
create_symlink(
    TRACK_DIR / "track-guard.py",
    HOME_DIR / ".claude" / "hooks" / "track-guard.py",
)
