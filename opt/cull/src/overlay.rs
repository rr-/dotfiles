use sdl3::{
    pixels::Color,
    render::{BlendMode, Canvas, FPoint, FRect},
    video::Window,
};

pub fn border(canvas: &mut Canvas<Window>, rect: FRect, thickness: f32) -> Result<(), String> {
    for edge in [
        FRect::new(rect.x, rect.y, rect.w, thickness),
        FRect::new(rect.x, rect.y + rect.h - thickness, rect.w, thickness),
        FRect::new(rect.x, rect.y, thickness, rect.h),
        FRect::new(rect.x + rect.w - thickness, rect.y, thickness, rect.h),
    ] {
        canvas.fill_rect(edge).map_err(|error| error.to_string())?;
    }
    Ok(())
}

pub fn outline(
    canvas: &mut Canvas<Window>,
    points: &[FPoint],
    thickness: f32,
) -> Result<(), String> {
    let pixels = thickness.round().max(1.0) as i32;
    for y in 0..pixels {
        for x in 0..pixels {
            let offset = (pixels - 1) as f32 / 2.0;
            let shifted: Vec<_> = points
                .iter()
                .map(|point| FPoint::new(point.x + x as f32 - offset, point.y + y as f32 - offset))
                .collect();
            canvas
                .draw_lines(shifted.as_slice())
                .map_err(|error| error.to_string())?;
        }
    }
    Ok(())
}

/// A see-through black box whose edge fades out instead of ending in a line.
pub fn panel(canvas: &mut Canvas<Window>, rect: FRect, dpi: f32) -> Result<(), String> {
    // The layers straddle the edge and stack to 75% black inside it:
    // 1 - (1 - 28/255)^12 ≈ 0.75.
    let layers = 12;
    canvas.set_blend_mode(BlendMode::Blend);
    canvas.set_draw_color(Color::RGBA(0, 0, 0, 28));
    for layer in 0..layers {
        let grow = (layer as f32 - layers as f32 / 2.0) * dpi;
        canvas
            .fill_rect(FRect::new(
                rect.x - grow,
                rect.y - grow,
                rect.w + grow * 2.0,
                rect.h + grow * 2.0,
            ))
            .map_err(|error| error.to_string())?;
    }
    canvas.set_blend_mode(BlendMode::None);
    Ok(())
}
