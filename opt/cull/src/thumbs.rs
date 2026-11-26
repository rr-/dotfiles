//! Small filmstrip previews kept on disk for a day, so coming back to a
//! folder shows its strip before anything is decoded again.

use crate::viewer::{Image, parse_frame};
use std::{
    hash::{Hash, Hasher},
    io::Write,
    os::unix::fs::MetadataExt,
    path::{Path, PathBuf},
    time::{Duration, SystemTime},
};

const LIFETIME: Duration = Duration::from_secs(86400);
/// Big enough for the filmstrip slot at 3x scale.
const MAX_WIDTH: u32 = 288;
const MAX_HEIGHT: u32 = 192;

fn dir() -> Option<PathBuf> {
    let base = std::env::var_os("XDG_CACHE_HOME")
        .filter(|value| !value.is_empty())
        .map(PathBuf::from)
        .or_else(|| std::env::var_os("HOME").map(|home| PathBuf::from(home).join(".cache")))?;
    Some(base.join("cull").join("thumbnails"))
}

/// Where the preview of a file lives; a changed file gets a new one.
fn location(path: &Path) -> Option<PathBuf> {
    let metadata = std::fs::metadata(path).ok()?;
    let mut hasher = std::collections::hash_map::DefaultHasher::new();
    path.hash(&mut hasher);
    metadata.len().hash(&mut hasher);
    metadata.mtime().hash(&mut hasher);
    metadata.mtime_nsec().hash(&mut hasher);
    Some(dir()?.join(format!("{:016x}.pam", hasher.finish())))
}

/// Delete previews older than a day.
pub fn prune() {
    let Some(dir) = dir() else { return };
    let Ok(entries) = std::fs::read_dir(dir) else {
        return;
    };
    let now = SystemTime::now();
    for entry in entries.flatten() {
        let old = entry
            .metadata()
            .and_then(|metadata| metadata.modified())
            .is_ok_and(|modified| now.duration_since(modified).unwrap_or_default() > LIFETIME);
        if old {
            let _ = std::fs::remove_file(entry.path());
        }
    }
}

pub fn load(path: &Path) -> Option<Image> {
    parse_frame(std::fs::read(location(path)?).ok()?).ok()
}

/// Save a shrunken copy of a decoded image; failures only cost a later decode.
pub fn store(path: &Path, image: &Image) {
    let Some(destination) = location(path) else {
        return;
    };
    if destination.exists() {
        return;
    }
    let small = shrink(image);
    let Some(parent) = destination.parent() else {
        return;
    };
    if std::fs::create_dir_all(parent).is_err() {
        return;
    }
    let temporary = destination.with_extension(format!("{}.tmp", std::process::id()));
    let written = std::fs::File::create(&temporary).and_then(|mut file| {
        write!(
            file,
            "P7\nWIDTH {}\nHEIGHT {}\nDEPTH 4\nMAXVAL 255\nTUPLTYPE RGB_ALPHA\nENDHDR\n",
            small.width, small.height
        )?;
        file.write_all(&small.pixels)
    });
    if written
        .and_then(|()| std::fs::rename(&temporary, &destination))
        .is_err()
    {
        let _ = std::fs::remove_file(&temporary);
    }
}

/// Fit within MAX_WIDTH × MAX_HEIGHT, averaging each source block.
fn shrink(image: &Image) -> Image {
    let scale = (MAX_WIDTH as f64 / image.width as f64)
        .min(MAX_HEIGHT as f64 / image.height as f64)
        .min(1.0);
    let width = ((image.width as f64 * scale).round() as u32).max(1);
    let height = ((image.height as f64 * scale).round() as u32).max(1);
    let mut pixels = Vec::with_capacity(width as usize * height as usize * 4);
    for y in 0..height {
        let top = (y as u64 * image.height as u64 / height as u64) as u32;
        let bottom = (((y + 1) as u64 * image.height as u64 / height as u64) as u32).max(top + 1);
        for x in 0..width {
            let left = (x as u64 * image.width as u64 / width as u64) as u32;
            let right = (((x + 1) as u64 * image.width as u64 / width as u64) as u32).max(left + 1);
            let mut sum = [0_u64; 4];
            for source_y in top..bottom {
                let row = source_y as usize * image.width as usize;
                for source_x in left..right {
                    let index = (row + source_x as usize) * 4;
                    for (channel, total) in sum.iter_mut().enumerate() {
                        *total += image.pixels[index + channel] as u64;
                    }
                }
            }
            let count = ((bottom - top) * (right - left)) as u64;
            pixels.extend(sum.map(|total| (total / count) as u8));
        }
    }
    Image {
        width,
        height,
        pixels,
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn shrink_fits_and_averages() {
        let image = Image {
            width: 576,
            height: 2,
            pixels: (0..576 * 2)
                .flat_map(|i| [(i % 2 * 255) as u8, 0, 0, 255])
                .collect(),
        };
        let small = shrink(&image);
        assert_eq!((small.width, small.height), (288, 1));
        assert_eq!(small.pixels.len(), 288 * 4);
        assert!(
            small
                .pixels
                .chunks(4)
                .all(|pixel| pixel == [127, 0, 0, 255])
        );
    }
}
