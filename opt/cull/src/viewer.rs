use crate::{
    commands::{self, Command as Action, Filter},
    files,
};
use sdl3::{
    pixels::{Color, PixelFormat},
    render::{FRect, ScaleMode},
};
use std::{
    collections::HashMap,
    io::Read,
    path::PathBuf,
    process::Command,
    sync::mpsc,
    time::{Duration, Instant},
};

struct Image {
    width: u32,
    height: u32,
    pixels: Vec<u8>,
}

fn decode(path: &PathBuf) -> Result<Image, String> {
    let decoded = Command::new("ffmpeg")
        .args(["-v", "error", "-threads", "2", "-i"])
        .arg(path)
        .args([
            "-frames:v",
            "1",
            "-c:v",
            "pam",
            "-f",
            "image2pipe",
            "-pix_fmt",
            "rgba",
            "-",
        ])
        .output()
        .map_err(|error| error.to_string())?;
    if !decoded.status.success() {
        return Err(String::from_utf8_lossy(&decoded.stderr).into_owned());
    }
    parse_frame(decoded.stdout)
}

/// Use the dimensions attached to the decoded pixels, after FFmpeg has
/// applied EXIF orientation. Probed source dimensions can be transposed while
/// retaining the same byte count, silently corrupting raw RGBA row strides.
fn parse_frame(mut data: Vec<u8>) -> Result<Image, String> {
    let marker = b"ENDHDR\n";
    let end = data
        .windows(marker.len())
        .take(4096)
        .position(|bytes| bytes == marker)
        .ok_or("missing decoded frame header")?
        + marker.len();
    let header = std::str::from_utf8(&data[..end]).map_err(|error| error.to_string())?;
    if !header.starts_with("P7\n") {
        return Err("unexpected frame format".into());
    }
    let field = |name: &str| -> Result<u32, String> {
        header
            .lines()
            .find_map(|line| line.strip_prefix(name))
            .ok_or_else(|| format!("missing {name}"))?
            .trim()
            .parse()
            .map_err(|_| format!("invalid {name}"))
    };
    let width = field("WIDTH ")?;
    let height = field("HEIGHT ")?;
    if field("DEPTH ")? != 4 || field("MAXVAL ")? != 255 {
        return Err("unexpected frame pixel format".into());
    }
    let size = (width as usize)
        .checked_mul(height as usize)
        .and_then(|size| size.checked_mul(4))
        .ok_or("frame dimensions overflow")?;
    if width == 0 || height == 0 || data.len() - end != size {
        return Err("incomplete decoded frame".into());
    }
    data.drain(..end);
    Ok(Image {
        width,
        height,
        pixels: data,
    })
}

#[cfg(test)]
mod frame_tests {
    use super::*;

    #[test]
    fn decoded_dimensions_determine_row_stride() {
        let mut data =
            b"P7\nWIDTH 2\nHEIGHT 3\nDEPTH 4\nMAXVAL 255\nTUPLTYPE RGB_ALPHA\nENDHDR\n".to_vec();
        data.extend(0..24);
        let image = parse_frame(data).unwrap();
        assert_eq!((image.width, image.height), (2, 3));
        assert_eq!(image.pixels, (0..24).collect::<Vec<u8>>());
    }
}

pub fn run() -> Result<(), String> {
    let mut paths = Vec::new();
    let mut selected = None;
    let mut recurse = false;
    let mut arguments = std::env::args().skip(1);
    while let Some(argument) = arguments.next() {
        match argument.as_str() {
            "--help" | "-h" => {
                println!(
                    "cull [--recurse] [--select FILE] [--playlist FILE|-] [PATH ...]\nNavigation: j/k, 10j/10k, gg first, G last, 100G jump to image 100\nView: v toggle original, p toggle pixel peek, f fullscreen, Alt+1/2/3 fit/fill/original, Z reset, +/-; HJKL pan, Alt+h/l rotate\nOverlays: c zoom overview; i image details; b filmstrip, filename and counter\nCull: S or ], x discard, X undo; zs slideshow\nClipboard: yp or Ctrl+c full path; yy image bitmap\nEscape cancels a pending numeric count or key sequence."
                );
                return Ok(());
            }
            "-r" | "--recurse" => recurse = true,
            "-s" | "--select" | "--vifm" => {
                selected = Some(
                    PathBuf::from(arguments.next().ok_or("missing selected path")?)
                        .canonicalize()
                        .map_err(|error| error.to_string())?,
                );
            }
            "-" | "--playlist" => {
                let name = arguments.next().ok_or("missing playlist")?;
                let text = if name == "-" {
                    let mut text = String::new();
                    std::io::stdin()
                        .read_to_string(&mut text)
                        .map_err(|error| error.to_string())?;
                    text
                } else {
                    std::fs::read_to_string(name).map_err(|error| error.to_string())?
                };
                for line in text.lines() {
                    files::scan(std::path::Path::new(line), recurse, &mut paths)?;
                }
            }
            _ => files::scan(std::path::Path::new(&argument), recurse, &mut paths)?,
        }
    }
    if paths.is_empty() {
        files::scan(
            selected
                .as_ref()
                .and_then(|path| path.parent())
                .unwrap_or(std::path::Path::new(".")),
            recurse,
            &mut paths,
        )?;
    }
    paths.sort();
    paths.dedup();
    if paths.is_empty() {
        return Err("no supported files".into());
    }
    let mut index = selected
        .and_then(|path| paths.iter().position(|candidate| *candidate == path))
        .unwrap_or(0);
    let sdl = sdl3::init().map_err(|error| error.to_string())?;
    let video = sdl.video().map_err(|error| error.to_string())?;
    let window = video
        .window("cull", 1280, 720)
        .resizable()
        .hidden()
        .fullscreen()
        .build()
        .map_err(|error| error.to_string())?;
    let mut canvas = window.into_canvas();
    let creator = canvas.texture_creator();
    let mut text = crate::text::Text::new(&creator, "sans-serif")?;
    let mut details_text = crate::text::Text::new(&creator, "monospace")?;
    let mut events = sdl.event_pump().map_err(|error| error.to_string())?;
    let (sender, receiver) = mpsc::channel();
    let mut pending = std::collections::HashSet::new();
    let mut cache = HashMap::new();
    let mut undo: Vec<(usize, PathBuf, files::Renames)> = Vec::new();
    let mut mode = 0;
    let mut previous_view = 0;
    let mut previous_pixel_view = 0;
    let mut aspect = 1.0_f32;
    let (mut zoom, mut pan_x, mut pan_y, mut rotation) = (0.0_f32, 0.0_f32, 0.0_f32, 0.0_f64);
    let mut fullscreen = true;
    let mut status = true;
    let mut slide = false;
    let mut interval = 0.3_f64;
    let mut changed = Instant::now();
    let mut message = String::new();
    let mut animation = None;
    let mut animation_path = PathBuf::new();
    let mut frame_at = Instant::now();
    let mut exif = false;
    let mut metadata = String::new();
    let mut metadata_path = PathBuf::new();
    let mut crop = true;
    let mut filters = crate::filters::Filters::default();
    let mut visible = false;
    let mut dirty = true;
    let mut osd: Option<(String, Instant)> = None;
    let mut input = commands::Input::default();
    'app: loop {
        if paths.is_empty() {
            break;
        }
        let (output_width, _) = canvas.output_size().map_err(|error| error.to_string())?;
        let radius = (output_width as usize / 130).max(6);
        for offset in std::iter::once(0_isize)
            .chain((1..=radius).flat_map(|distance| [distance as isize, -(distance as isize)]))
        {
            let candidate = index as isize + offset;
            if candidate < 0 || candidate as usize >= paths.len() {
                continue;
            }
            let path = paths[candidate as usize].clone();
            if cache.contains_key(&path) || pending.len() >= 3 || !pending.insert(path.clone()) {
                continue;
            }
            let sender = sender.clone();
            std::thread::spawn(move || {
                let result = decode(&path);
                let _ = sender.send((path, result));
            });
        }
        while let Ok((path, result)) = receiver.try_recv() {
            dirty = true;
            pending.remove(&path);
            match result {
                Ok(image) => {
                    let mut texture = creator
                        .create_texture_static(PixelFormat::RGBA32, image.width, image.height)
                        .map_err(|error| error.to_string())?;
                    texture
                        .update(None, &image.pixels, image.width as usize * 4)
                        .map_err(|error| error.to_string())?;
                    cache.insert(
                        path,
                        (texture, image.width, image.height, image.pixels, 0_u64),
                    );
                }
                Err(error) => message = error,
            }
        }
        if cache.len() > radius * 2 + 2 {
            cache.retain(|path, _| {
                paths[index.saturating_sub(radius)..(index + radius + 1).min(paths.len())]
                    .contains(path)
                    // Undo restores this original path, so retain its decoded
                    // pixels and uploaded texture even after leaving the area.
                    || undo.last().is_some_and(|(_, removed, _)| removed == path)
            });
        }
        let mut actions = Vec::new();
        for event in events.poll_iter() {
            dirty = true;
            if let Some(command) = input.event(&event, events_keyboard_ctrl()) {
                actions.push(command);
            }
        }
        for command in actions {
            dirty = true;
            {
                let old_index = index;
                match command {
                    Action::Quit => break 'app,
                    Action::Fullscreen => {
                        fullscreen = !fullscreen;
                        canvas
                            .window_mut()
                            .set_fullscreen(fullscreen)
                            .map_err(|error| error.to_string())?;
                    }
                    Action::Rotate(delta) => rotation += delta,
                    Action::Pan(x, y) => {
                        pan_x += x;
                        pan_y += y;
                    }
                    Action::Navigate(delta) => {
                        index = index.saturating_add_signed(delta).min(paths.len() - 1)
                    }
                    Action::First => index = 0,
                    Action::Last => index = paths.len() - 1,
                    Action::Jump(position) => index = position.min(paths.len() - 1),
                    Action::Filter(filter, delta) => {
                        match filter {
                            Filter::Contrast => filters.contrast += delta,
                            Filter::Brightness => filters.brightness += delta,
                            Filter::Gamma => filters.gamma += delta,
                            Filter::Saturation => filters.saturation += delta,
                        }
                        filters.revision += 1;
                    }
                    Action::View(_) | Action::TogglePixel | Action::ToggleOriginal => {
                        mode = match command {
                            Action::View(value) => value,
                            Action::TogglePixel if mode == 3 => previous_pixel_view,
                            Action::TogglePixel => {
                                previous_pixel_view = mode;
                                3
                            }
                            Action::ToggleOriginal if mode == 2 => previous_view,
                            Action::ToggleOriginal => {
                                previous_view = mode;
                                2
                            }
                            _ => unreachable!(),
                        };
                        zoom = if mode == 3 { 3.0 } else { 0.0 };
                        pan_x = 0.0;
                        pan_y = 0.0;
                        rotation = 0.0;
                    }
                    Action::Interval(delta) => interval = (interval + delta).max(0.1),
                    Action::Zoom(delta) => zoom += delta,
                    Action::Status => status = !status,
                    Action::Blur(value) => {
                        filters.blur = value;
                        filters.revision += 1;
                    }
                    Action::Aspect(delta) => aspect = (aspect + delta).max(0.05),
                    Action::ResetAspect => aspect = 1.0,
                    Action::Exif => exif = !exif,
                    Action::Overview => crop = !crop,
                    Action::Slideshow => {
                        slide = !slide;
                        changed = Instant::now();
                    }
                    Action::CopyPath => {
                        video
                            .clipboard()
                            .set_clipboard_text(&paths[index].to_string_lossy())
                            .map_err(|error| error.to_string())?;
                        message = "Copied full path".into();
                    }
                    Action::CopyBitmap => {
                        if let Some((_, width, height, pixels, _)) = cache.get(&paths[index]) {
                            message = match crate::clipboard::copy_bitmap(
                                &filters.apply(pixels, *width),
                                *width,
                                *height,
                            ) {
                                Ok(()) => "Copied image".into(),
                                Err(error) => error,
                            };
                        } else {
                            message = "Image still loading".into();
                        }
                    }
                    Action::Select => {
                        let result = files::group(&paths[index], false).and_then(|renames| {
                            files::rename_group(&renames)?;
                            Ok(renames)
                        });
                        match result {
                            Ok(renames) => {
                                for (old, new) in renames {
                                    if let Some(image) = cache.remove(&old) {
                                        cache.insert(new.clone(), image);
                                    }
                                    for path in &mut paths {
                                        if *path == old {
                                            *path = new.clone();
                                        }
                                    }
                                }
                            }
                            Err(error) => message = error,
                        }
                    }
                    Action::Undo => {
                        if let Some((position, path, renames)) = undo.last() {
                            let reversed = renames
                                .iter()
                                .map(|(old, new)| (new.clone(), old.clone()))
                                .collect();
                            match files::rename_group(&reversed) {
                                Ok(()) => {
                                    let position = (*position).min(paths.len());
                                    let path = path.clone();
                                    paths.insert(position, path);
                                    index = position;
                                    undo.pop();
                                }
                                Err(error) => message = error,
                            }
                        }
                    }
                    Action::Discard => {
                        let result = files::group(&paths[index], true).and_then(|renames| {
                            files::rename_group(&renames)?;
                            Ok(renames)
                        });
                        match result {
                            Ok(renames) => {
                                let path = paths.remove(index);
                                undo.push((index, path, renames));
                                index = index.min(paths.len().saturating_sub(1));
                            }
                            Err(error) => message = error,
                        }
                    }
                    Action::FileManager => {
                        let _ = Command::new("vifm").arg(&paths[index]).spawn();
                    }
                    Action::CopyHome => {
                        if let Some(home) = std::env::var_os("HOME") {
                            let destination = PathBuf::from(home)
                                .join(paths[index].file_name().ok_or("missing filename")?);
                            match std::fs::OpenOptions::new()
                                .write(true)
                                .create_new(true)
                                .open(&destination)
                            {
                                Ok(mut output) => {
                                    let result =
                                        std::fs::File::open(&paths[index]).and_then(|mut input| {
                                            std::io::copy(&mut input, &mut output)
                                        });
                                    message = match result {
                                        Ok(_) => format!("Copied to {}", destination.display()),
                                        Err(error) => error.to_string(),
                                    };
                                }
                                Err(error) => message = error.to_string(),
                            }
                        }
                    }
                    Action::MoveHome => {
                        if let Some(home) = std::env::var_os("HOME") {
                            let destination = PathBuf::from(home)
                                .join(paths[index].file_name().ok_or("missing filename")?);
                            match files::rename_group(&vec![(paths[index].clone(), destination)]) {
                                Ok(()) => {
                                    paths.remove(index);
                                    index = index.min(paths.len().saturating_sub(1));
                                }
                                Err(error) => message = error,
                            }
                        }
                    }
                }
                if index != old_index {
                    changed = Instant::now();
                    message.clear();
                }
                let feedback = match command {
                    Action::Filter(filter, _) => {
                        let (name, value) = match filter {
                            Filter::Contrast => ("Contrast", filters.contrast),
                            Filter::Brightness => ("Brightness", filters.brightness),
                            Filter::Gamma => ("Gamma", filters.gamma),
                            Filter::Saturation => ("Saturation", filters.saturation),
                        };
                        Some(format!("{name}: {:+.0}", value * 100.0))
                    }
                    Action::Blur(_) => {
                        Some(format!("Blur: {}", if filters.blur { "on" } else { "off" }))
                    }
                    Action::Zoom(_) => Some(format!("Zoom: {:.2}x", zoom.exp2())),
                    Action::View(_) | Action::TogglePixel | Action::ToggleOriginal => {
                        Some(format!(
                            "View: {}",
                            match mode {
                                0 => "Fit",
                                1 => "Fill",
                                2 => "Original (1:1)",
                                _ => "Pixel",
                            }
                        ))
                    }
                    Action::CopyBitmap | Action::CopyPath => Some(message.clone()),
                    _ => None,
                };
                if let Some(feedback) = feedback {
                    osd = Some((feedback, Instant::now()));
                }
            }
        }
        if paths.is_empty() {
            break;
        }
        if slide && changed.elapsed().as_secs_f64() >= interval && cache.contains_key(&paths[index])
        {
            if index + 1 < paths.len() {
                index += 1;
                changed = Instant::now();
                dirty = true;
            } else {
                slide = false;
            }
        }
        let animation_ready =
            animation.is_some() && frame_at.elapsed() >= Duration::from_secs_f64(1.0 / 30.0);
        if osd
            .as_ref()
            .is_some_and(|(_, started)| started.elapsed() >= Duration::from_millis(1400))
        {
            osd = None;
            dirty = true;
        }
        if !dirty && !animation_ready {
            std::thread::sleep(Duration::from_millis(8));
            continue;
        }
        if !visible && !cache.contains_key(&paths[index]) && message.is_empty() {
            std::thread::sleep(Duration::from_millis(8));
            continue;
        }
        dirty = false;
        let (window_width, window_height) =
            canvas.output_size().map_err(|error| error.to_string())?;
        let (logical_width, _) = canvas.window().size();
        let dpi = canvas
            .window()
            .display_scale()
            .max(window_width as f32 / logical_width.max(1) as f32)
            .max(1.0);
        let strip_height = if status { 80.0 * dpi } else { 0.0 };
        let viewport_height = (window_height as f32 - strip_height).max(1.0);
        let border_width = dpi.round().max(1.0);
        let mut overview_bounds = None;
        canvas.set_draw_color(Color::RGB(16, 16, 16));
        canvas.clear();
        if animation_path != paths[index] {
            animation = None;
            animation_path = paths[index].clone();
        }
        if exif && metadata_path != paths[index] {
            metadata_path = paths[index].clone();
            metadata = Command::new("exiftool")
                .args([
                    "-s",
                    "-ImageWidth",
                    "-ImageHeight",
                    "-FocalLength",
                    "-ExposureTime",
                    "-Aperture",
                    "-ISO",
                    "-Model",
                    "-LensModel",
                ])
                .arg(&paths[index])
                .output()
                .map(|output| String::from_utf8_lossy(&output.stdout).into_owned())
                .unwrap_or_else(|error| error.to_string());
        }
        if let Some((texture, width, height, pixels, revision)) = cache.get_mut(&paths[index]) {
            if *revision != filters.revision {
                texture
                    .update(None, &filters.apply(pixels, *width), *width as usize * 4)
                    .map_err(|error| error.to_string())?;
                *revision = filters.revision;
            }
            let extension = paths[index]
                .extension()
                .unwrap_or_default()
                .to_string_lossy()
                .to_lowercase();
            if animation.is_none() && ["gif", "webm", "mp4", "mkv"].contains(&extension.as_str()) {
                animation = crate::animation::Animation::open(&paths[index], *width, *height).ok();
            }
            if frame_at.elapsed() >= Duration::from_secs_f64(1.0 / 30.0)
                && let Some(animation) = &animation
                && let Ok(pixels) = animation.frames.try_recv()
            {
                texture
                    .update(None, &pixels, *width as usize * 4)
                    .map_err(|error| error.to_string())?;
                frame_at = Instant::now();
            }
            let ww = window_width;
            let wh = viewport_height;
            let sx = ww as f32 / (*width as f32 * aspect);
            let sy = wh as f32 / *height as f32;
            let scale = match mode {
                1 => sx.max(sy),
                2 | 3 => 1.0,
                _ => sx.min(sy),
            } * zoom.exp2();
            texture.set_scale_mode(if mode == 3 {
                ScaleMode::Nearest
            } else {
                ScaleMode::Linear
            });
            let rect = FRect::new(
                (ww as f32 - *width as f32 * scale * aspect) / 2.0 + pan_x * ww as f32,
                (wh as f32 - *height as f32 * scale) / 2.0 + pan_y * wh as f32,
                *width as f32 * scale * aspect,
                *height as f32 * scale,
            );
            canvas.set_clip_rect(sdl3::rect::Rect::new(
                0,
                0,
                window_width,
                viewport_height as u32,
            ));
            canvas
                .copy_ex(texture, None, rect, rotation, None, false, false)
                .map_err(|error| error.to_string())?;
            canvas.set_clip_rect(None);
            if crop {
                // Invert the image transform for each screen corner. This
                // keeps the overview accurate when panning and rotating.
                let overview_scale =
                    (220.0 * dpi / *width as f32).min(160.0 * dpi / *height as f32);
                let overview_width = *width as f32 * overview_scale;
                let overview_height = *height as f32 * overview_scale;
                let left = ww as f32 - overview_width - 20.0 * dpi;
                let top = viewport_height - 12.0 * dpi - overview_height;
                let overview = FRect::new(left, top, overview_width, overview_height);
                overview_bounds = Some(overview);
                canvas.set_draw_color(Color::RGB(30, 30, 30));
                canvas
                    .fill_rect(FRect::new(
                        left - 5.0 * dpi,
                        top - 5.0 * dpi,
                        overview_width + 10.0 * dpi,
                        overview_height + 10.0 * dpi,
                    ))
                    .map_err(|error| error.to_string())?;
                canvas
                    .copy(texture, None, overview)
                    .map_err(|error| error.to_string())?;
                canvas.set_draw_color(Color::WHITE);
                crate::overlay::border(&mut canvas, overview, border_width)?;
                let angle = -(rotation as f32).to_radians();
                let (sin, cos) = angle.sin_cos();
                let center_x = rect.x + rect.w / 2.0;
                let center_y = rect.y + rect.h / 2.0;
                let corners = [
                    (0.0, 0.0),
                    (ww as f32, 0.0),
                    (ww as f32, wh as f32),
                    (0.0, wh as f32),
                    (0.0, 0.0),
                ];
                let points: Vec<sdl3::render::FPoint> = corners
                    .iter()
                    .map(|(x, y)| {
                        let dx = x - center_x;
                        let dy = y - center_y;
                        let image_x = ((dx * cos - dy * sin) / scale + *width as f32 / 2.0)
                            .clamp(0.0, *width as f32);
                        let image_y = ((dx * sin + dy * cos) / scale + *height as f32 / 2.0)
                            .clamp(0.0, *height as f32);
                        sdl3::render::FPoint::new(
                            left + image_x * overview_scale,
                            top + image_y * overview_scale,
                        )
                    })
                    .collect();
                canvas.set_draw_color(Color::RGB(255, 255, 0));
                crate::overlay::outline(&mut canvas, points.as_slice(), border_width)?;
            }
        }
        let font_size = 26.0 * dpi;
        if status {
            canvas.set_draw_color(Color::RGB(20, 20, 20));
            canvas
                .fill_rect(FRect::new(
                    0.0,
                    window_height as f32 - strip_height,
                    window_width as f32,
                    strip_height,
                ))
                .map_err(|error| error.to_string())?;
            let slots = (window_width as f32 / (104.0 * dpi)).floor().max(1.0) as usize;
            let slot_width = window_width as f32 / slots as f32;
            let thumbnail_height = 64.0 * dpi;
            let thumbnail_width = thumbnail_height * 1.5;
            let visible_count = slots;
            let start = index
                .saturating_sub(visible_count / 2)
                .min(paths.len().saturating_sub(visible_count));
            for slot_index in 0..slots {
                let candidate = start + slot_index;
                let path = paths.get(candidate);
                let left = slot_index as f32 * slot_width + (slot_width - thumbnail_width) / 2.0;
                let top = window_height as f32 - strip_height + 6.4 * dpi;
                let slot = FRect::new(left, top, thumbnail_width, thumbnail_height);
                if let Some((texture, width, height, _, _)) = path.and_then(|path| cache.get(path))
                {
                    let scale =
                        (thumbnail_width / *width as f32).min(thumbnail_height / *height as f32);
                    let destination = FRect::new(
                        left + (thumbnail_width - *width as f32 * scale) / 2.0,
                        top + (thumbnail_height - *height as f32 * scale) / 2.0,
                        *width as f32 * scale,
                        *height as f32 * scale,
                    );
                    canvas
                        .copy(texture, None, destination)
                        .map_err(|error| error.to_string())?;
                }
                canvas.set_draw_color(if candidate == index {
                    Color::RGB(255, 210, 60)
                } else {
                    Color::RGB(65, 65, 65)
                });
                crate::overlay::border(&mut canvas, slot, border_width)?;
            }
        }
        if exif {
            details_text.draw(&mut canvas, &metadata, 20.0 * dpi, 20.0 * dpi, font_size)?;
        }
        if status {
            let caption = paths[index]
                .file_name()
                .unwrap_or_default()
                .to_string_lossy();
            text.draw(
                &mut canvas,
                &caption,
                20.0 * dpi,
                window_height as f32 - strip_height - 42.0 * dpi,
                font_size,
            )?;
            let counter = format!("{} / {}", index + 1, paths.len());
            let counter_width = text.width(&counter, font_size);
            let (counter_x, counter_y) = overview_bounds.map_or(
                (
                    window_width as f32 - counter_width - 20.0 * dpi,
                    window_height as f32 - strip_height - 42.0 * dpi,
                ),
                |overview| {
                    (
                        overview.x - counter_width - 20.0 * dpi,
                        overview.y + overview.h - font_size,
                    )
                },
            );
            text.draw(&mut canvas, &counter, counter_x, counter_y, font_size)?;
        }
        if let Some((feedback, _)) = &osd {
            let size = 22.0 * dpi;
            let left = (window_width as f32 - text.width(feedback, size)) / 2.0;
            text.draw(&mut canvas, feedback, left, 24.0 * dpi, size)?;
        }
        canvas.present();
        if !visible {
            canvas.window_mut().show();
            visible = true;
            dirty = true;
        }
        std::thread::sleep(Duration::from_millis(8));
    }
    Ok(())
}

fn events_keyboard_ctrl() -> bool {
    // SDL's modifier state is independent of the event queue borrow.
    let modifiers = unsafe { sdl3::sys::keyboard::SDL_GetModState() };
    modifiers.0 & 0x00c0 != 0
}
