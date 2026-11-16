use std::path::{Path, PathBuf};

pub fn supported(path: &Path) -> bool {
    path.extension()
        .and_then(|value| value.to_str())
        .is_some_and(|extension| {
            [
                "jpg", "jpeg", "svg", "jfif", "gif", "png", "tga", "pcx", "bmp", "webm", "webp",
                "mkv", "mp4", "psd", "tif", "tiff", "ico", "avif", "jxl",
            ]
            .iter()
            .any(|known| extension.eq_ignore_ascii_case(known))
        })
}

pub fn scan(path: &Path, recurse: bool, output: &mut Vec<PathBuf>) -> Result<(), String> {
    if path.is_dir() {
        for entry in std::fs::read_dir(path).map_err(|error| error.to_string())? {
            let entry = entry.map_err(|error| error.to_string())?.path();
            if entry.is_file() || recurse {
                scan(&entry, recurse, output)?;
            }
        }
    } else if path.is_file() && supported(path) {
        output.push(path.canonicalize().map_err(|error| error.to_string())?);
    }
    Ok(())
}

/// Order paths the way people count: digit runs compare as numbers, so
/// IMG_9 sorts before IMG_10.
pub fn natural_cmp(a: &Path, b: &Path) -> std::cmp::Ordering {
    fn chunks(text: &str) -> Vec<(bool, &str)> {
        let mut result = Vec::new();
        let mut start = 0;
        let bytes = text.as_bytes();
        for i in 1..=bytes.len() {
            if i == bytes.len() || bytes[i].is_ascii_digit() != bytes[start].is_ascii_digit() {
                result.push((bytes[start].is_ascii_digit(), &text[start..i]));
                start = i;
            }
        }
        result
    }
    let (a, b) = (a.to_string_lossy(), b.to_string_lossy());
    for (left, right) in chunks(&a).into_iter().zip(chunks(&b)) {
        let order = match (left, right) {
            ((true, left), (true, right)) => {
                let (left, right) = (left.trim_start_matches('0'), right.trim_start_matches('0'));
                left.len().cmp(&right.len()).then_with(|| left.cmp(right))
            }
            ((left_digit, left), (right_digit, right)) => {
                right_digit.cmp(&left_digit).then_with(|| left.cmp(right))
            }
        };
        if order.is_ne() {
            return order;
        }
    }
    a.cmp(&b)
}

fn stem(path: &Path) -> String {
    path.file_stem()
        .unwrap_or_default()
        .to_string_lossy()
        .trim_end_matches("-SELECTED")
        .to_owned()
}

pub type Renames = Vec<(PathBuf, PathBuf)>;

pub fn group(path: &Path, discard: bool) -> Result<Renames, String> {
    let selected = path
        .file_stem()
        .unwrap_or_default()
        .to_string_lossy()
        .ends_with("-SELECTED");
    let mut result = Vec::new();
    for entry in std::fs::read_dir(path.parent().ok_or("missing parent")?)
        .map_err(|error| error.to_string())?
    {
        let source = entry.map_err(|error| error.to_string())?.path();
        if !source.is_file() || stem(&source) != stem(path) {
            continue;
        }
        let destination = if discard {
            source.with_file_name(format!(
                "{}~",
                source.file_name().unwrap().to_string_lossy()
            ))
        } else {
            source.with_file_name(format!(
                "{}{}.{}",
                stem(&source),
                if selected { "" } else { "-SELECTED" },
                source.extension().unwrap_or_default().to_string_lossy()
            ))
        };
        result.push((source, destination));
    }
    Ok(result)
}

/// How a discarded group went away, so undo knows how to bring it back.
pub enum Discarded {
    /// Into the trash; the ids of its items.
    Trashed(Vec<PathBuf>),
    /// Renamed aside with a ~, where the trash wouldn't take it.
    Renamed(Renames),
}

/// Trash path and the files sharing its stem, or failing that rename them
/// aside with a ~. The second value says why the trash wasn't used.
pub fn discard(path: &Path) -> Result<(Discarded, Option<String>), String> {
    let renames = group(path, true)?;
    let mut ids = Vec::new();
    let mut failure = None;
    for (source, _) in &renames {
        match trash::put(source) {
            Ok(entry) => ids.push(entry.id),
            Err(error) => {
                failure = Some(error);
                break;
            }
        }
    }
    let Some(failure) = failure else {
        return Ok((Discarded::Trashed(ids), None));
    };
    // a group goes as one, so put back what did make it into the trash
    for id in ids.iter().rev() {
        trash::restore(id)?;
    }
    rename_group(&renames)?;
    Ok((
        Discarded::Renamed(renames),
        Some(format!("Not trashed ({failure}), renamed with ~")),
    ))
}

pub fn undo_discard(discarded: &Discarded) -> Result<(), String> {
    match discarded {
        Discarded::Trashed(ids) => {
            for id in ids {
                trash::restore(id)?;
            }
            Ok(())
        }
        Discarded::Renamed(renames) => rename_group(
            &renames
                .iter()
                .map(|(old, new)| (new.clone(), old.clone()))
                .collect(),
        ),
    }
}

pub fn rename_group(renames: &Renames) -> Result<(), String> {
    for (source, destination) in renames {
        if source != destination && destination.exists() {
            return Err(format!("refusing to overwrite {}", destination.display()));
        }
    }
    let mut completed: Renames = Vec::new();
    for (source, destination) in renames {
        if source == destination {
            continue;
        }
        if let Err(error) = rename_noreplace(source, destination) {
            let mut errors = vec![error.to_string()];
            for (old, new) in completed.iter().rev() {
                if let Err(error) = rename_noreplace(new, old) {
                    errors.push(error.to_string());
                }
            }
            return Err(errors.join("; "));
        }
        completed.push((source.clone(), destination.clone()));
    }
    Ok(())
}

fn rename_noreplace(source: &Path, destination: &Path) -> std::io::Result<()> {
    use std::os::unix::ffi::OsStrExt;
    let c_source = std::ffi::CString::new(source.as_os_str().as_bytes())?;
    let c_destination = std::ffi::CString::new(destination.as_os_str().as_bytes())?;
    let result = unsafe {
        libc::renameat2(
            libc::AT_FDCWD,
            c_source.as_ptr(),
            libc::AT_FDCWD,
            c_destination.as_ptr(),
            libc::RENAME_NOREPLACE,
        )
    };
    if result == 0 {
        return Ok(());
    }
    let error = std::io::Error::last_os_error();
    // FUSE filesystems such as sshfs can't refuse an overwrite themselves, so
    // look before renaming there; rename_group has looked once already
    if error.raw_os_error() == Some(libc::EINVAL) {
        if destination.exists() {
            return Err(std::io::ErrorKind::AlreadyExists.into());
        }
        return std::fs::rename(source, destination);
    }
    Err(error)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn natural_order_counts_digit_runs() {
        let mut paths: Vec<PathBuf> = [
            "a/IMG_10.jpg",
            "a/IMG_9.jpg",
            "a/IMG_009b.jpg",
            "a/IMG_1.jpg",
            "a/IMG_.jpg",
        ]
        .iter()
        .map(PathBuf::from)
        .collect();
        paths.sort_by(|a, b| natural_cmp(a, b));
        let names: Vec<_> = paths.iter().map(|path| path.to_str().unwrap()).collect();
        assert_eq!(
            names,
            [
                "a/IMG_1.jpg",
                "a/IMG_9.jpg",
                "a/IMG_009b.jpg",
                "a/IMG_10.jpg",
                "a/IMG_.jpg"
            ]
        );
    }

    #[test]
    fn discard_trashes_the_whole_group_and_undo_brings_it_back() {
        let root = std::env::temp_dir().join(format!("cull-discard-{}", std::process::id()));
        let _ = std::fs::remove_dir_all(&root);
        std::fs::create_dir_all(root.join("shoot")).unwrap();
        // safe: the only test that touches the environment
        unsafe {
            std::env::set_var("XDG_DATA_HOME", root.join("data"));
            std::env::set_var("XDG_STATE_HOME", root.join("state"));
        }
        let jpeg = root.join("shoot/DSC_1.JPG");
        let raw = root.join("shoot/DSC_1.NEF");
        let other = root.join("shoot/DSC_2.JPG");
        for path in [&jpeg, &raw, &other] {
            std::fs::write(path, "").unwrap();
        }

        let (discarded, note) = discard(&jpeg).unwrap();
        assert!(note.is_none());
        let Discarded::Trashed(ids) = &discarded else {
            panic!("renamed rather than trashed");
        };
        assert_eq!(ids.len(), 2);
        assert!(!jpeg.exists() && !raw.exists() && other.exists());

        undo_discard(&discarded).unwrap();
        assert!(jpeg.exists() && raw.exists());
        std::fs::remove_dir_all(&root).unwrap();
    }

    #[test]
    fn collision_does_not_overwrite_and_failed_group_rolls_back() {
        let root = std::env::temp_dir().join(format!("cull-transactions-{}", std::process::id()));
        std::fs::create_dir_all(&root).unwrap();
        let first = root.join("first.jpg");
        let second = root.join("second.jpg");
        std::fs::write(&first, b"first").unwrap();
        std::fs::write(&second, b"second").unwrap();
        assert!(rename_group(&vec![(first.clone(), second.clone())]).is_err());
        assert_eq!(std::fs::read(&second).unwrap(), b"second");
        let moved = root.join("moved.jpg");
        assert!(
            rename_group(&vec![
                (first.clone(), moved.clone()),
                (root.join("missing"), root.join("target"))
            ])
            .is_err()
        );
        assert!(first.exists());
        assert!(!moved.exists());
        std::fs::remove_file(first).unwrap();
        std::fs::remove_file(second).unwrap();
        std::fs::remove_dir(root).unwrap();
    }
}
