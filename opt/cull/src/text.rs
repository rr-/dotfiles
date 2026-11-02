use fontdue::{Font, FontSettings};
use sdl3::{
    pixels::PixelFormat,
    render::{Canvas, FRect, Texture, TextureCreator},
    video::{Window, WindowContext},
};

pub struct Text<'a> {
    font: Font,
    creator: &'a TextureCreator<WindowContext>,
    cached: std::collections::HashMap<(String, u32), (Texture<'a>, u32, u32)>,
}

impl<'a> Text<'a> {
    pub fn width(&self, text: &str, size: f32) -> f32 {
        text.chars()
            .map(|character| self.font.metrics(character, size).advance_width)
            .sum()
    }

    pub fn new(creator: &'a TextureCreator<WindowContext>, family: &str) -> Result<Self, String> {
        let output = std::process::Command::new("fc-match")
            .args(["-f", "%{file}", family])
            .output()
            .map_err(|error| error.to_string())?;
        let path = String::from_utf8_lossy(&output.stdout);
        let bytes = std::fs::read(path.trim()).map_err(|error| error.to_string())?;
        let font =
            Font::from_bytes(bytes, FontSettings::default()).map_err(|error| error.to_string())?;
        Ok(Self {
            font,
            creator,
            cached: Default::default(),
        })
    }

    pub fn draw(
        &mut self,
        canvas: &mut Canvas<Window>,
        text: &str,
        x: f32,
        y: f32,
        size: f32,
    ) -> Result<(), String> {
        let key = (text.to_owned(), size.round() as u32);
        if !self.cached.contains_key(&key) {
            if self.cached.len() > 64 {
                self.cached.clear();
            }
            let lines: Vec<_> = text.lines().collect();
            let width = lines
                .iter()
                .map(|line| {
                    line.chars()
                        .map(|character| self.font.metrics(character, size).advance_width)
                        .sum::<f32>()
                        .ceil() as u32
                })
                .max()
                .unwrap_or(1)
                .max(1);
            let height = ((lines.len().max(1) as f32 + 0.3) * size * 1.4).ceil() as u32;
            let mut pixels = vec![0_u8; width as usize * height as usize * 4];
            for (line_number, line) in lines.iter().enumerate() {
                let mut pen = 0.0;
                for character in line.chars() {
                    let (metrics, bitmap) = self.font.rasterize(character, size);
                    let top = (line_number as f32 * size * 1.4 + size) as i32
                        - metrics.height as i32
                        - metrics.ymin;
                    for row in 0..metrics.height {
                        for column in 0..metrics.width {
                            let dx = pen as i32 + metrics.xmin + column as i32;
                            let dy = top + row as i32;
                            if dx < 0 || dy < 0 || dx >= width as i32 || dy >= height as i32 {
                                continue;
                            }
                            let index = (dy as usize * width as usize + dx as usize) * 4;
                            pixels[index..index + 4].copy_from_slice(&[
                                255,
                                255,
                                255,
                                bitmap[row * metrics.width + column],
                            ]);
                        }
                    }
                    pen += metrics.advance_width;
                }
            }
            let mut texture = self
                .creator
                .create_texture_static(PixelFormat::RGBA32, width, height)
                .map_err(|error| error.to_string())?;
            texture.set_blend_mode(sdl3::render::BlendMode::Blend);
            texture
                .update(None, &pixels, width as usize * 4)
                .map_err(|error| error.to_string())?;
            self.cached.insert(key.clone(), (texture, width, height));
        }
        let (texture, width, height) = self.cached.get_mut(&key).expect("text cached above");
        texture.set_color_mod(0, 0, 0);
        canvas
            .copy(
                texture,
                None,
                FRect::new(x + 2.0, y + 2.0, *width as f32, *height as f32),
            )
            .map_err(|error| error.to_string())?;
        texture.set_color_mod(255, 255, 255);
        canvas
            .copy(
                texture,
                None,
                FRect::new(x, y, *width as f32, *height as f32),
            )
            .map_err(|error| error.to_string())
    }
}
