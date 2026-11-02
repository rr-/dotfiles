use std::{
    io::Write,
    process::{Command, Stdio},
};

pub fn copy_bitmap(pixels: &[u8], width: u32, height: u32) -> Result<(), String> {
    let mut bytes = Vec::new();
    {
        let mut encoder = png::Encoder::new(&mut bytes, width, height);
        encoder.set_color(png::ColorType::Rgba);
        encoder.set_depth(png::BitDepth::Eight);
        encoder.set_compression(png::Compression::Fast);
        let mut writer = encoder.write_header().map_err(|error| error.to_string())?;
        writer
            .write_image_data(pixels)
            .map_err(|error| error.to_string())?;
    }
    // xclip implements the X11 INCR protocol for images larger than a single
    // X_ChangeProperty request. Both helpers retain ownership after cull exits.
    let mut command = if std::env::var_os("WAYLAND_DISPLAY").is_some() {
        let mut command = Command::new("wl-copy");
        command.args(["--type", "image/png"]);
        command
    } else {
        let mut command = Command::new("xclip");
        command.args(["-selection", "clipboard", "-t", "image/png", "-i"]);
        command
    };
    let mut child = command
        .stdin(Stdio::piped())
        .stdout(Stdio::null())
        .stderr(Stdio::null())
        .spawn()
        .map_err(|error| format!("clipboard helper: {error}"))?;
    let result = child
        .stdin
        .take()
        .ok_or("missing clipboard input")?
        .write_all(&bytes);
    let status = child.wait().map_err(|error| error.to_string())?;
    result.map_err(|error| error.to_string())?;
    if status.success() {
        Ok(())
    } else {
        Err(format!("clipboard helper exited with {status}"))
    }
}
