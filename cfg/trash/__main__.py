from libdotfiles.util import HOME_DIR, REPO_ROOT_DIR, create_symlink, run

project_dir = REPO_ROOT_DIR / "opt" / "trash"
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
    project_dir / "target" / "release" / "trash",
    HOME_DIR / ".local" / "bin" / "trash",
)
