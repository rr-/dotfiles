//! The vifm cull was opened from, reached through its client-server mode.

use std::path::Path;
use std::process::{Command, Stdio};

fn remote() -> Command {
    let mut command = Command::new("vifm");
    if let Some(server) = std::env::var_os("VIFM_SERVER_NAME") {
        command.arg("--server-name").arg(server);
    }
    command
}

/// Quote a path for the shell vifm hands a `:!` command to, with vifm's own
/// `%` macros escaped first.
fn quote(path: &Path) -> String {
    let text = path.to_string_lossy().replace('%', "%%");
    format!("'{}'", text.replace('\'', r"'\''"))
}

/// Have the vifm that opened cull start it again on its own listing of the
/// current view, so the files come in vifm's order rather than a fresh scan's.
/// False where cull wasn't started from a vifm.
pub fn relaunch(selected: &Path) -> bool {
    if std::env::var_os("VIFM_SERVER_NAME").is_none() {
        return false;
    }
    remote()
        .arg("--remote")
        .arg(format!(
            "+%!cull --select {} --playlist - %Pl >/dev/null 2>&1 &",
            quote(selected)
        ))
        .status()
        .is_ok_and(|status| status.success())
}

/// Select path in vifm's current pane, leaving the other pane where it is,
/// or open a vifm on it where none is running.
pub fn reveal(path: &Path) {
    let running = Command::new("pidof")
        .arg("vifm")
        .stdout(Stdio::null())
        .status()
        .is_ok_and(|status| status.success());
    if !running {
        let _ = Command::new("wezterm")
            .args(["start", "--", "vifm", "--select"])
            .arg(path)
            .spawn();
        return;
    }

    // vifm --remote fills the left pane from its first path, so where the
    // right pane is current the left one is handed back its own directory
    let info = remote()
        .args(["--remote-expr", r#"paneisat("left").expand("\n%D")"#])
        .output()
        .map(|output| String::from_utf8_lossy(&output.stdout).replace('\\', ""))
        .unwrap_or_default();
    let mut lines = info.lines();
    let left_is_current = lines.next() == Some("1");
    let mut command = remote();
    command.arg("--remote");
    if !left_is_current && let Some(other_dir) = lines.next() {
        command.arg(other_dir);
    }
    let _ = command.arg("--select").arg(path).spawn();
}
