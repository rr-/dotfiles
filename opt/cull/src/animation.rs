use std::{
    io::Read,
    path::Path,
    process::{Child, Command, Stdio},
    sync::mpsc::{self, Receiver},
};

/// Bounded streaming keeps long animations from consuming the image cache.
pub struct Animation {
    child: Child,
    pub frames: Receiver<Vec<u8>>,
}

impl Animation {
    pub fn open(path: &Path, width: u32, height: u32) -> Result<Self, String> {
        let mut child = Command::new("ffmpeg")
            .args(["-v", "error", "-threads", "2", "-stream_loop", "-1", "-i"])
            .arg(path)
            .args(["-vf", "fps=30", "-f", "rawvideo", "-pix_fmt", "rgba", "-"])
            .stdout(Stdio::piped())
            .stderr(Stdio::null())
            .spawn()
            .map_err(|error| error.to_string())?;
        let mut stdout = child.stdout.take().ok_or("missing animation output")?;
        let (sender, frames) = mpsc::sync_channel(2);
        std::thread::spawn(move || {
            loop {
                let mut pixels = vec![0; width as usize * height as usize * 4];
                if stdout.read_exact(&mut pixels).is_err() || sender.send(pixels).is_err() {
                    break;
                }
            }
        });
        Ok(Self { child, frames })
    }
}

impl Drop for Animation {
    fn drop(&mut self) {
        let _ = self.child.kill();
        let _ = self.child.wait();
    }
}
