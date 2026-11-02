#[derive(Default)]
pub struct Filters {
    pub contrast: f32,
    pub brightness: f32,
    pub gamma: f32,
    pub saturation: f32,
    pub revision: u64,
    pub blur: bool,
}

impl Filters {
    pub fn apply(&self, source: &[u8], width: u32) -> Vec<u8> {
        let mut result = source.to_vec();
        let mut table = [0_u8; 256];
        for (index, value) in table.iter_mut().enumerate() {
            let level = ((index as f32 / 255.0 - 0.5) * (1.0 + self.contrast).max(0.0)
                + 0.5
                + self.brightness)
                .clamp(0.0, 1.0);
            *value = (level.powf(1.0 / (1.0 + self.gamma).max(0.01)) * 255.0).round() as u8;
        }
        for pixel in result.as_chunks_mut::<4>().0 {
            let gray =
                0.2126 * pixel[0] as f32 + 0.7152 * pixel[1] as f32 + 0.0722 * pixel[2] as f32;
            for channel in &mut pixel[..3] {
                let saturated = (gray + (*channel as f32 - gray) * (1.0 + self.saturation).max(0.0))
                    .clamp(0.0, 255.0) as usize;
                *channel = table[saturated];
            }
        }
        if self.blur && width > 1 {
            let original = result.clone();
            let stride = width as usize * 4;
            for index in stride..result.len().saturating_sub(stride) {
                if index % 4 == 3 || index % stride < 4 || index % stride >= stride - 4 {
                    continue;
                }
                result[index] = ((original[index] as u32 * 4
                    + original[index - 4] as u32
                    + original[index + 4] as u32
                    + original[index - stride] as u32
                    + original[index + stride] as u32)
                    / 8) as u8;
            }
        }
        result
    }
}
