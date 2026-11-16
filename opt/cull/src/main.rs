mod animation;
mod clipboard;
mod commands;
mod files;
mod filters;
mod overlay;
mod text;
mod viewer;
mod vifm;

fn main() {
    if let Err(error) = viewer::run() {
        eprintln!("cull: {error}");
        std::process::exit(1);
    }
}
