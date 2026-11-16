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
