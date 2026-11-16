//! The freedesktop.org trash, https://specifications.freedesktop.org/trash-spec/,
//! without the parts that need a desktop: no daemon, and no scanning of every
//! mount, which hangs on a network mount whose host is down. Only the trashes
//! this crate has put something in are ever looked at again.
//!
//! What it writes is the spec's own layout, so a file manager, trash-cli or a
//! plain mv can still recover anything put away here.

use std::fs::{self, DirBuilder, OpenOptions};
use std::io::{self, Write};
use std::os::unix::ffi::{OsStrExt, OsStringExt};
use std::os::unix::fs::{DirBuilderExt, MetadataExt, OpenOptionsExt, PermissionsExt};
use std::path::{Component, Path, PathBuf};

/// One trashed item.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Entry {
    /// Where the item lives now, `<trash>/files/<name>`; doubles as its id.
    pub id: PathBuf,
    /// Where it was trashed from.
    pub original: PathBuf,
    /// When, the way the spec writes it: local time, `YYYY-MM-DDThh:mm:ss`.
    pub deleted: String,
}

fn uid() -> u32 {
    unsafe { libc::getuid() }
}

fn xdg_dir(variable: &str, fallback: &str) -> Result<PathBuf, String> {
    if let Some(dir) = std::env::var_os(variable).filter(|dir| !dir.is_empty()) {
        return Ok(dir.into());
    }
    std::env::var_os("HOME")
        .map(|home| PathBuf::from(home).join(fallback))
        .ok_or_else(|| "HOME is not set".into())
}

/// The trash for everything on the same filesystem as the home directory.
pub fn home_trash() -> Result<PathBuf, String> {
    Ok(xdg_dir("XDG_DATA_HOME", ".local/share")?.join("Trash"))
}

fn state_dir() -> Result<PathBuf, String> {
    Ok(xdg_dir("XDG_STATE_HOME", ".local/state")?.join("trash"))
}

/// The device of path, or of its nearest existing ancestor where it doesn't
/// exist yet, as a trash about to be made doesn't.
fn device(path: &Path) -> io::Result<u64> {
    let mut path = path;
    loop {
        match fs::metadata(path) {
            Ok(metadata) => return Ok(metadata.dev()),
            Err(error) if error.kind() == io::ErrorKind::NotFound => {
                path = path.parent().ok_or(error)?;
            }
            Err(error) => return Err(error),
        }
    }
}

/// The root of the mount dir is on: the last ancestor still on its device.
fn topdir(dir: &Path, dev: u64) -> PathBuf {
    let mut top = dir;
    while let Some(parent) = top.parent() {
        match fs::metadata(parent) {
            Ok(metadata) if metadata.dev() == dev => top = parent,
            _ => break,
        }
    }
    top.to_path_buf()
}

/// Make trash's files and info directories, private to the user. A trash that
/// is already there has to be a real directory of the user's own, so nobody
/// else can have planted it to read what gets deleted.
fn ensure(trash: &Path) -> Result<(), String> {
    if let Ok(metadata) = fs::symlink_metadata(trash)
        && (!metadata.is_dir() || metadata.uid() != uid())
    {
        return Err(format!("{} is not a directory of yours", trash.display()));
    }
    for part in ["files", "info"] {
        DirBuilder::new()
            .recursive(true)
            .mode(0o700)
            .create(trash.join(part))
            .map_err(|error| format!("cannot make {}: {error}", trash.display()))?;
    }
    Ok(())
}

/// The trash an item in dir on device dev goes to, and the topdir its path
/// is written relative to, if any.
fn trash_for(dir: &Path, dev: u64) -> Result<(PathBuf, Option<PathBuf>), String> {
    let home = home_trash()?;
    if device(&home).map_err(|error| error.to_string())? == dev {
        ensure(&home)?;
        return Ok((home, None));
    }
    let top = topdir(dir, dev);
    // $topdir/.Trash/$uid, where an admin made .Trash a sticky directory
    let admin = top.join(".Trash");
    if let Ok(metadata) = fs::symlink_metadata(&admin)
        && metadata.is_dir()
        && metadata.permissions().mode() & 0o1000 != 0
    {
        let trash = admin.join(uid().to_string());
        if ensure(&trash).is_ok() {
            return Ok((trash, Some(top)));
        }
    }
    let trash = top.join(format!(".Trash-{}", uid()));
    ensure(&trash)?;
    Ok((trash, Some(top)))
}

/// The topdir a trash's relative paths start from: the parent of a
/// `.Trash-$uid`, the grandparent of a `.Trash/$uid`, none for the home trash.
fn topdir_of(trash: &Path) -> Option<&Path> {
    let parent = trash.parent()?;
    if trash.file_name()?.to_string_lossy().starts_with(".Trash-") {
        return Some(parent);
    }
    if parent.file_name()? == ".Trash" {
        return parent.parent();
    }
    None
}

fn encode(bytes: &[u8]) -> String {
    let mut text = String::new();
    for &byte in bytes {
        if byte.is_ascii_alphanumeric() || b"-_.~/".contains(&byte) {
            text.push(byte as char);
        } else {
            text.push_str(&format!("%{byte:02X}"));
        }
    }
    text
}

fn decode(text: &str) -> Result<Vec<u8>, String> {
    let bytes = text.as_bytes();
    let mut output = Vec::with_capacity(bytes.len());
    let mut i = 0;
    while i < bytes.len() {
        if bytes[i] == b'%' {
            let hex = text
                .get(i + 1..i + 3)
                .and_then(|hex| u8::from_str_radix(hex, 16).ok())
                .ok_or_else(|| format!("bad escape in {text}"))?;
            output.push(hex);
            i += 3;
        } else {
            output.push(bytes[i]);
            i += 1;
        }
    }
    Ok(output)
}

fn now() -> String {
    date_ago(0)
}

/// Local time seconds ago, written the way a DeletionDate is, so the two sort
/// against each other as text.
pub fn date_ago(seconds: i64) -> String {
    unsafe {
        let time = libc::time(std::ptr::null_mut()) - seconds;
        let mut tm: libc::tm = std::mem::zeroed();
        libc::localtime_r(&time, &mut tm);
        format!(
            "{:04}-{:02}-{:02}T{:02}:{:02}:{:02}",
            tm.tm_year + 1900,
            tm.tm_mon + 1,
            tm.tm_mday,
            tm.tm_hour,
            tm.tm_min,
            tm.tm_sec
        )
    }
}

/// Remember trash, so list and empty know to look in it.
fn record(trash: &Path) -> Result<(), String> {
    let state = state_dir()?;
    fs::create_dir_all(&state).map_err(|error| error.to_string())?;
    let file = state.join("dirs");
    let known = fs::read(&file).unwrap_or_default();
    let line = trash.as_os_str().as_bytes();
    if known
        .split(|&byte| byte == b'\n')
        .any(|known| known == line)
    {
        return Ok(());
    }
    let mut output = OpenOptions::new()
        .append(true)
        .create(true)
        .open(&file)
        .map_err(|error| error.to_string())?;
    output
        .write_all(&[line, b"\n"].concat())
        .map_err(|error| error.to_string())
}

/// The home trash and every trash this crate has put something in.
pub fn trashes() -> Result<Vec<PathBuf>, String> {
    let mut trashes = vec![home_trash()?];
    let known = fs::read(state_dir()?.join("dirs")).unwrap_or_default();
    for line in known
        .split(|&byte| byte == b'\n')
        .filter(|line| !line.is_empty())
    {
        let trash = PathBuf::from(std::ffi::OsString::from_vec(line.to_vec()));
        if !trashes.contains(&trash) {
            trashes.push(trash);
        }
    }
    Ok(trashes)
}

/// Move path into the trash for its filesystem. A symlink goes in itself,
/// not what it points at.
pub fn put(path: &Path) -> Result<Entry, String> {
    let name = path
        .file_name()
        .ok_or_else(|| format!("cannot trash {}", path.display()))?;
    let metadata =
        fs::symlink_metadata(path).map_err(|error| format!("{}: {error}", path.display()))?;
    let parent = match path.parent() {
        Some(parent) if !parent.as_os_str().is_empty() => parent,
        _ => Path::new("."),
    };
    let original = parent
        .canonicalize()
        .map_err(|error| error.to_string())?
        .join(name);
    let (trash, top) = trash_for(original.parent().unwrap(), metadata.dev())?;
    if original.starts_with(&trash) {
        return Err(format!("{} is in the trash already", original.display()));
    }
    let written = match &top {
        Some(top) => original.strip_prefix(top).unwrap(),
        None => &original,
    };
    let deleted = now();
    let info_text = format!(
        "[Trash Info]\nPath={}\nDeletionDate={deleted}\n",
        encode(written.as_os_str().as_bytes())
    );

    // a name is taken by making its info file, which only one of two trashes
    // racing for the same name can do
    for n in 1.. {
        let mut stored = name.to_os_string();
        if n > 1 {
            stored.push(format!(".{n}"));
        }
        let id = trash.join("files").join(&stored);
        if fs::symlink_metadata(&id).is_ok() {
            continue;
        }
        let mut info_name = stored.clone();
        info_name.push(".trashinfo");
        let info = trash.join("info").join(info_name);
        let mut file = match OpenOptions::new()
            .write(true)
            .create_new(true)
            .mode(0o600)
            .open(&info)
        {
            Ok(file) => file,
            Err(error) if error.kind() == io::ErrorKind::AlreadyExists => continue,
            Err(error) => return Err(format!("{}: {error}", info.display())),
        };
        let moved = file
            .write_all(info_text.as_bytes())
            .and_then(|()| fs::rename(&original, &id));
        if let Err(error) = moved {
            let _ = fs::remove_file(&info);
            return Err(format!("{}: {error}", original.display()));
        }
        record(&trash)?;
        return Ok(Entry {
            id,
            original,
            deleted,
        });
    }
    unreachable!()
}

fn info_path(id: &Path) -> Result<PathBuf, String> {
    let bad = || format!("{} is not in a trash", id.display());
    let files = id.parent().ok_or_else(bad)?;
    if files.file_name() != Some("files".as_ref()) {
        return Err(bad());
    }
    let mut name = id.file_name().ok_or_else(bad)?.to_os_string();
    name.push(".trashinfo");
    Ok(files.parent().ok_or_else(bad)?.join("info").join(name))
}

/// Read the entry whose item lives at id.
pub fn entry(id: &Path) -> Result<Entry, String> {
    let info = info_path(id)?;
    let text = fs::read_to_string(&info).map_err(|error| format!("{}: {error}", info.display()))?;
    let value = |key: &str| {
        text.lines()
            .find_map(|line| line.strip_prefix(key)?.strip_prefix('='))
            .map(str::trim)
    };
    let written = PathBuf::from(std::ffi::OsString::from_vec(decode(
        value("Path").ok_or_else(|| format!("{} has no Path", info.display()))?,
    )?));
    let original = if written.is_absolute() {
        written
    } else {
        // nothing in a relative path may climb out of the topdir
        if !written
            .components()
            .all(|component| matches!(component, Component::Normal(_)))
        {
            return Err(format!("{} has a bad Path", info.display()));
        }
        let trash = info.parent().and_then(Path::parent).unwrap();
        topdir_of(trash)
            .ok_or_else(|| format!("{} has a relative Path", info.display()))?
            .join(written)
    };
    Ok(Entry {
        id: id.to_path_buf(),
        original,
        deleted: value("DeletionDate").unwrap_or_default().to_owned(),
    })
}

/// Put the item at id back where it came from, making its directory again if
/// it's gone. Refuses to overwrite anything already there.
pub fn restore(id: &Path) -> Result<PathBuf, String> {
    let entry = entry(id)?;
    if fs::symlink_metadata(&entry.original).is_ok() {
        return Err(format!("{} exists already", entry.original.display()));
    }
    if let Some(parent) = entry.original.parent() {
        fs::create_dir_all(parent).map_err(|error| error.to_string())?;
    }
    fs::rename(id, &entry.original).map_err(|error| format!("{}: {error}", id.display()))?;
    fs::remove_file(info_path(id)?).map_err(|error| error.to_string())?;
    Ok(entry.original)
}

/// Everything in the trashes this crate knows of, oldest first.
pub fn list() -> Result<Vec<Entry>, String> {
    let mut entries = Vec::new();
    for trash in trashes()? {
        let Ok(infos) = fs::read_dir(trash.join("info")) else {
            continue;
        };
        for info in infos.flatten() {
            let name = info.file_name();
            let Some(stem) = name.as_bytes().strip_suffix(b".trashinfo") else {
                continue;
            };
            let id = trash.join("files").join(std::ffi::OsStr::from_bytes(stem));
            if let Ok(entry) = entry(&id) {
                entries.push(entry);
            }
        }
    }
    entries.sort_by(|a, b| a.deleted.cmp(&b.deleted));
    Ok(entries)
}

/// Delete an entry for good: the item, then its info file.
pub fn purge(entry: &Entry) -> Result<(), String> {
    let removed = match fs::symlink_metadata(&entry.id) {
        Ok(metadata) if metadata.is_dir() => fs::remove_dir_all(&entry.id),
        Ok(_) => fs::remove_file(&entry.id),
        Err(error) if error.kind() == io::ErrorKind::NotFound => Ok(()),
        Err(error) => Err(error),
    };
    removed.map_err(|error| format!("{}: {error}", entry.id.display()))?;
    fs::remove_file(info_path(&entry.id)?).map_err(|error| error.to_string())
}

/// What a trash holds.
#[derive(Debug, Default, Clone, Copy, PartialEq, Eq)]
pub struct Usage {
    pub items: u64,
    /// Disk space taken, counted the way du does: allocated blocks, not
    /// apparent sizes, with symlinks not followed.
    pub bytes: u64,
}

fn disk_usage(path: &Path) -> io::Result<u64> {
    let metadata = match fs::symlink_metadata(path) {
        Ok(metadata) => metadata,
        Err(error) if error.kind() == io::ErrorKind::NotFound => return Ok(0),
        Err(error) => return Err(error),
    };
    let mut bytes = metadata.blocks() * 512;
    if metadata.is_dir() {
        for entry in fs::read_dir(path)? {
            bytes += disk_usage(&entry?.path())?;
        }
    }
    Ok(bytes)
}

/// What one trash holds; one that isn't there holds nothing.
pub fn usage(trash: &Path) -> Result<Usage, String> {
    let items = match fs::read_dir(trash.join("info")) {
        Ok(infos) => infos
            .flatten()
            .filter(|info| info.file_name().as_bytes().ends_with(b".trashinfo"))
            .count() as u64,
        Err(_) => 0,
    };
    let files = trash.join("files");
    let bytes = disk_usage(&files).map_err(|error| format!("{}: {error}", files.display()))?;
    Ok(Usage { items, bytes })
}

/// Remember the ids of the last batch put away, for restoring it as one.
pub fn set_last(ids: &[PathBuf]) -> Result<(), String> {
    let state = state_dir()?;
    fs::create_dir_all(&state).map_err(|error| error.to_string())?;
    let text: Vec<u8> = ids
        .iter()
        .flat_map(|id| [id.as_os_str().as_bytes(), b"\n"].concat())
        .collect();
    fs::write(state.join("last"), text).map_err(|error| error.to_string())
}

pub fn last() -> Result<Vec<PathBuf>, String> {
    let text = fs::read(state_dir()?.join("last")).unwrap_or_default();
    Ok(text
        .split(|&byte| byte == b'\n')
        .filter(|line| !line.is_empty())
        .map(|line| PathBuf::from(std::ffi::OsString::from_vec(line.to_vec())))
        .collect())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn paths_encode_and_decode() {
        let path = "dir/a b%c/ąę#.png";
        let encoded = encode(path.as_bytes());
        assert_eq!(encoded, "dir/a%20b%25c/%C4%85%C4%99%23.png");
        assert_eq!(decode(&encoded).unwrap(), path.as_bytes());
        assert!(decode("%2").is_err());
    }

    #[test]
    fn topdirs_follow_both_layouts() {
        assert_eq!(
            topdir_of(Path::new("/mnt/x/.Trash-1000")),
            Some(Path::new("/mnt/x"))
        );
        assert_eq!(
            topdir_of(Path::new("/mnt/x/.Trash/1000")),
            Some(Path::new("/mnt/x"))
        );
        assert_eq!(topdir_of(Path::new("/home/u/.local/share/Trash")), None);
    }

    #[test]
    fn ids_must_sit_in_a_files_directory() {
        assert!(info_path(Path::new("/t/files/a.png")).is_ok());
        assert!(info_path(Path::new("/t/other/a.png")).is_err());
    }

    /// Put, collide, restore and purge in a home trash under a scratch dir.
    #[test]
    fn put_restore_and_purge_round_trip() {
        let root = std::env::temp_dir().join(format!("trash-test-{}", std::process::id()));
        let _ = fs::remove_dir_all(&root);
        fs::create_dir_all(root.join("work")).unwrap();
        // safe: the only test that touches the environment
        unsafe {
            std::env::set_var("XDG_DATA_HOME", root.join("data"));
            std::env::set_var("XDG_STATE_HOME", root.join("state"));
        }
        let file = root.join("work/a b.png");

        fs::write(&file, "one").unwrap();
        let first = put(&file).unwrap();
        fs::write(&file, "two").unwrap();
        let second = put(&file).unwrap();
        assert!(!file.exists());
        assert_eq!(first.id, root.join("data/Trash/files/a b.png"));
        assert_eq!(second.id, root.join("data/Trash/files/a b.png.2"));
        assert_eq!(entry(&second.id).unwrap().original, file);
        assert_eq!(list().unwrap().len(), 2);
        let usage = usage(&root.join("data/Trash")).unwrap();
        assert_eq!(usage.items, 2);
        assert!(usage.bytes > 0);

        assert_eq!(restore(&second.id).unwrap(), file);
        assert_eq!(fs::read_to_string(&file).unwrap(), "two");
        assert!(restore(&first.id).is_err(), "restore overwrote a file");

        purge(&first).unwrap();
        assert!(list().unwrap().is_empty());
        fs::remove_dir_all(&root).unwrap();
    }
}
