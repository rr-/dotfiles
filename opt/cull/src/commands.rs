use sdl3::{
    event::Event,
    keyboard::{Keycode, Mod},
};

#[derive(Clone, Copy, Debug, PartialEq)]
pub enum Command {
    Quit,
    Fullscreen,
    Navigate(isize),
    First,
    Last,
    Jump(usize),
    Rotate(f64),
    Pan(f32, f32),
    View(u8),
    ToggleOriginal,
    TogglePixel,
    Zoom(f32),
    Interval(f64),
    Status,
    Blur(bool),
    Aspect(f32),
    ResetAspect,
    Exif,
    Overview,
    Slideshow,
    CopyPath,
    CopyBitmap,
    Select,
    Undo,
    Discard,
    FileManager,
    CopyHome,
    MoveHome,
    Filter(Filter, f32),
}

#[derive(Clone, Copy, Debug, PartialEq)]
pub enum Filter {
    Contrast,
    Brightness,
    Gamma,
    Saturation,
}

#[derive(Clone, Copy)]
pub struct Binding {
    pub key: Keycode,
    pub modifiers: u8,
    pub command: Command,
}

const SHIFT: u8 = 1;
const CTRL: u8 = 2;
const ALT: u8 = 4;

macro_rules! binding {
    ($key:ident, $modifiers:expr, $command:expr) => {
        Binding {
            key: Keycode::$key,
            modifiers: $modifiers,
            command: $command,
        }
    };
}

use Command::*;

pub const REGISTRY: &[Binding] = &[
    binding!(Q, 0, Quit),
    binding!(Q, CTRL, Quit),
    binding!(Escape, 0, Quit),
    binding!(F, 0, Fullscreen),
    binding!(V, 0, ToggleOriginal),
    binding!(J, 0, Navigate(1)),
    binding!(Space, 0, Navigate(1)),
    binding!(Right, 0, Navigate(1)),
    binding!(Apostrophe, 0, Navigate(1)),
    binding!(K, 0, Navigate(-1)),
    binding!(Backspace, 0, Navigate(-1)),
    binding!(Left, 0, Navigate(-1)),
    binding!(Semicolon, 0, Navigate(-1)),
    binding!(Home, 0, First),
    binding!(A, CTRL, First),
    binding!(End, 0, Last),
    binding!(E, CTRL, Last),
    binding!(H, ALT, Rotate(-45.0)),
    binding!(L, ALT, Rotate(45.0)),
    binding!(H, ALT | SHIFT, Rotate(-1.0)),
    binding!(L, ALT | SHIFT, Rotate(1.0)),
    binding!(H, SHIFT, Pan(0.01, 0.0)),
    binding!(L, SHIFT, Pan(-0.01, 0.0)),
    binding!(K, SHIFT, Pan(0.0, 0.01)),
    binding!(J, SHIFT, Pan(0.0, -0.01)),
    binding!(H, CTRL, Pan(0.1, 0.0)),
    binding!(L, CTRL, Pan(-0.1, 0.0)),
    binding!(K, CTRL, Pan(0.0, 0.1)),
    binding!(J, CTRL, Pan(0.0, -0.1)),
    binding!(_1, ALT, View(0)),
    binding!(_2, ALT, View(1)),
    binding!(_3, ALT, View(2)),
    binding!(Z, SHIFT, View(0)),
    binding!(Equals, 0, Zoom(0.03)),
    binding!(Equals, CTRL, Zoom(0.03)),
    binding!(Minus, 0, Zoom(-0.03)),
    binding!(Minus, CTRL, Zoom(-0.03)),
    binding!(Equals, ALT, Interval(0.025)),
    binding!(Minus, ALT, Interval(-0.025)),
    binding!(B, 0, Status),
    binding!(N, 0, Blur(true)),
    binding!(N, SHIFT, Blur(false)),
    binding!(LeftBracket, CTRL, Aspect(-0.05)),
    binding!(RightBracket, CTRL, Aspect(0.05)),
    binding!(A, 0, ResetAspect),
    binding!(A, SHIFT, ResetAspect),
    binding!(P, 0, TogglePixel),
    binding!(I, 0, Exif),
    binding!(C, 0, Overview),
    binding!(G, SHIFT, Last),
    binding!(C, CTRL, CopyPath),
    binding!(S, SHIFT, Select),
    binding!(RightBracket, 0, Select),
    binding!(X, SHIFT, Undo),
    binding!(X, 0, Discard),
    binding!(H, 0, FileManager),
    binding!(Return, 0, FileManager),
    binding!(LeftBracket, 0, CopyHome),
    binding!(LeftBracket, SHIFT, MoveHome),
    binding!(RightBracket, SHIFT, MoveHome),
    binding!(_1, SHIFT, Filter(Filter::Contrast, -0.01)),
    binding!(_2, SHIFT, Filter(Filter::Contrast, 0.01)),
    binding!(_3, SHIFT, Filter(Filter::Brightness, -0.01)),
    binding!(_4, SHIFT, Filter(Filter::Brightness, 0.01)),
    binding!(_5, SHIFT, Filter(Filter::Gamma, -0.01)),
    binding!(_6, SHIFT, Filter(Filter::Gamma, 0.01)),
    binding!(_7, SHIFT, Filter(Filter::Saturation, -0.01)),
    binding!(_8, SHIFT, Filter(Filter::Saturation, 0.01)),
];

pub const SEQUENCES: &[(Keycode, Keycode, Command)] = &[
    (Keycode::Y, Keycode::P, CopyPath),
    (Keycode::Y, Keycode::Y, CopyBitmap),
    (Keycode::G, Keycode::G, First),
    (Keycode::Z, Keycode::S, Slideshow),
];

/// Numeric counts and multi-key commands have no timing dependency.
#[derive(Default)]
pub struct Input {
    count: Option<usize>,
    prefix: Option<Keycode>,
}

impl Input {
    pub fn event(&mut self, event: &Event, mouse_ctrl: bool) -> Option<Command> {
        if let Event::KeyDown {
            keycode: Some(key),
            keymod,
            repeat,
            ..
        } = event
        {
            return self.key(*key, *keymod, *repeat, std::time::Instant::now());
        }
        from_event(event, mouse_ctrl)
    }

    fn key(
        &mut self,
        key: Keycode,
        modifiers: Mod,
        repeat: bool,
        _now: std::time::Instant,
    ) -> Option<Command> {
        // Modifier presses are separate SDL key events. In particular,
        // Shift must not consume the numeric prefix before an uppercase G.
        if matches!(
            key,
            Keycode::LShift
                | Keycode::RShift
                | Keycode::LCtrl
                | Keycode::RCtrl
                | Keycode::LAlt
                | Keycode::RAlt
                | Keycode::LGui
                | Keycode::RGui
        ) {
            return None;
        }
        if key == Keycode::Escape && (self.count.is_some() || self.prefix.is_some()) {
            self.count = None;
            self.prefix = None;
            return None;
        }
        let modifiers = modifiers & !(Mod::CAPSMOD | Mod::NUMMOD);
        if modifiers.is_empty() {
            if let Some(prefix) = self.prefix.take() {
                if repeat {
                    self.prefix = Some(prefix);
                    return None;
                }
                let command = SEQUENCES
                    .iter()
                    .find(|(first, second, _)| *first == prefix && *second == key)
                    .map(|(_, _, command)| *command);
                let count = self.count.take();
                return command.map(|command| match (command, count) {
                    (First, Some(count)) => Jump(count.max(1) - 1),
                    _ => command,
                });
            }
            let digit = match key {
                Keycode::_0 => Some(0),
                Keycode::_1 => Some(1),
                Keycode::_2 => Some(2),
                Keycode::_3 => Some(3),
                Keycode::_4 => Some(4),
                Keycode::_5 => Some(5),
                Keycode::_6 => Some(6),
                Keycode::_7 => Some(7),
                Keycode::_8 => Some(8),
                Keycode::_9 => Some(9),
                _ => None,
            };
            if let Some(digit) = digit {
                if !repeat {
                    self.count = Some(
                        self.count
                            .unwrap_or(0)
                            .saturating_mul(10)
                            .saturating_add(digit),
                    );
                }
                return None;
            }
            if SEQUENCES.iter().any(|(first, _, _)| *first == key) {
                if repeat {
                    return None;
                }
                self.prefix = Some(key);
                return None;
            }
        }
        self.prefix = None;
        let count = self.count.take();
        let normalized = modifiers & !(Mod::CAPSMOD | Mod::NUMMOD);
        let mask = u8::from(normalized.intersects(Mod::LSHIFTMOD | Mod::RSHIFTMOD))
            | (u8::from(normalized.intersects(Mod::LCTRLMOD | Mod::RCTRLMOD)) << 1)
            | (u8::from(normalized.intersects(Mod::LALTMOD | Mod::RALTMOD)) << 2);
        let command = REGISTRY
            .iter()
            .find(|binding| binding.key == key && binding.modifiers == mask)?
            .command;
        if repeat
            && !matches!(
                command,
                Navigate(_) | Zoom(_) | Pan(..) | Rotate(_) | Filter(..)
            )
        {
            return None;
        }
        Some(match (command, count) {
            (Navigate(delta), Some(count)) => {
                Navigate(delta.saturating_mul(count.min(isize::MAX as usize) as isize))
            }
            (Last, Some(count)) => Jump(count.max(1) - 1),
            _ => command,
        })
    }
}

pub fn from_event(event: &Event, mouse_ctrl: bool) -> Option<Command> {
    match event {
        Event::Quit { .. } => Some(Quit),
        Event::KeyDown {
            keycode: Some(key),
            keymod,
            repeat,
            ..
        } => {
            let modifiers = u8::from(keymod.intersects(Mod::LSHIFTMOD | Mod::RSHIFTMOD))
                | (u8::from(keymod.intersects(Mod::LCTRLMOD | Mod::RCTRLMOD)) << 1)
                | (u8::from(keymod.intersects(Mod::LALTMOD | Mod::RALTMOD)) << 2);
            let command = REGISTRY
                .iter()
                .find(|binding| binding.key == *key && binding.modifiers == modifiers)?
                .command;
            if *repeat
                && !matches!(
                    command,
                    Navigate(_) | Zoom(_) | Pan(..) | Rotate(_) | Filter(..)
                )
            {
                return None;
            }
            Some(command)
        }
        Event::MouseWheel { y, .. } if *y != 0.0 => Some(if mouse_ctrl {
            Zoom(if *y > 0.0 { 0.03 } else { -0.03 })
        } else {
            Navigate(if *y > 0.0 { -1 } else { 1 })
        }),
        _ => None,
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn vim_counts_and_jumps() {
        let mut input = Input::default();
        let now = std::time::Instant::now();
        for key in [Keycode::_1, Keycode::_0] {
            assert_eq!(input.key(key, Mod::NOMOD, false, now), None);
        }
        assert_eq!(
            input.key(Keycode::J, Mod::NOMOD, false, now),
            Some(Navigate(10))
        );
        for key in [Keycode::_1, Keycode::_0, Keycode::_0] {
            input.key(key, Mod::NOMOD, false, now);
        }
        assert_eq!(
            input.key(Keycode::G, Mod::LSHIFTMOD, false, now),
            Some(Jump(99))
        );
        input.key(Keycode::_5, Mod::NOMOD, false, now);
        input.key(Keycode::_0, Mod::NOMOD, false, now);
        assert_eq!(input.key(Keycode::LShift, Mod::LSHIFTMOD, false, now), None);
        assert_eq!(
            input.key(Keycode::G, Mod::LSHIFTMOD, false, now),
            Some(Jump(49))
        );
        assert_eq!(input.key(Keycode::G, Mod::NOMOD, false, now), None);
        assert_eq!(input.key(Keycode::G, Mod::NOMOD, false, now), Some(First));
        assert_eq!(
            input.key(Keycode::G, Mod::LSHIFTMOD, false, now),
            Some(Last)
        );
        input.key(Keycode::Z, Mod::NOMOD, false, now);
        assert_eq!(
            input.key(Keycode::S, Mod::NOMOD, false, now),
            Some(Slideshow)
        );
        input.key(Keycode::Z, Mod::NOMOD, false, now);
        assert_eq!(input.key(Keycode::P, Mod::NOMOD, false, now), None);
        assert_eq!(
            input.key(Keycode::P, Mod::NOMOD, false, now),
            Some(TogglePixel)
        );
        assert_eq!(
            input.key(Keycode::V, Mod::NOMOD, false, now),
            Some(ToggleOriginal)
        );
        input.key(Keycode::Z, Mod::NOMOD, false, now);
        assert_eq!(input.key(Keycode::V, Mod::NOMOD, false, now), None);
    }

    #[test]
    fn view_shortcuts_and_clipboard_sequences() {
        let now = std::time::Instant::now();
        let mut input = Input::default();
        input.key(Keycode::_2, Mod::NOMOD, false, now);
        assert_eq!(
            input.key(
                Keycode::J,
                Mod::NOMOD,
                false,
                now + std::time::Duration::from_secs(60)
            ),
            Some(Navigate(2))
        );
        assert_eq!(
            input.key(Keycode::_2, Mod::LALTMOD, false, now),
            Some(View(1))
        );
        input.key(Keycode::Y, Mod::NOMOD, false, now);
        assert_eq!(
            input.key(Keycode::P, Mod::NOMOD, false, now),
            Some(CopyPath)
        );
        input.key(Keycode::Y, Mod::NOMOD, false, now);
        assert_eq!(
            input.key(Keycode::Y, Mod::NOMOD, false, now),
            Some(CopyBitmap)
        );
    }

    #[test]
    fn registry_has_no_conflicting_bindings() {
        for (index, binding) in REGISTRY.iter().enumerate() {
            assert!(
                !REGISTRY[..index]
                    .iter()
                    .any(|other| other.key == binding.key && other.modifiers == binding.modifiers)
            );
        }
    }
}
