use std::io::{BufRead, IsTerminal, Write};
use std::path::PathBuf;

const USAGE: &str = "\
trash put FILE...           move files to the trash, printing where each went
trash restore ID...         put items back where they came from
trash restore --last        put back the last batch put away
trash list                  date, original path and id of everything trashed
trash stat                  items and disk space in each trash
trash empty [--older DAYS] [--yes]
                            delete trashed items for good";

fn run() -> Result<(), String> {
    let mut arguments = std::env::args_os().skip(1);
    let command = arguments.next().ok_or(USAGE)?;
    let arguments: Vec<_> = arguments.collect();
    match command.to_str() {
        Some("put") => {
            if arguments.is_empty() {
                return Err(USAGE.into());
            }
            let mut ids = Vec::new();
            let mut failed = None;
            for path in &arguments {
                match trash::put(path.as_ref()) {
                    Ok(entry) => {
                        println!("{}", entry.id.display());
                        ids.push(entry.id);
                    }
                    Err(error) => failed = Some(error),
                }
            }
            trash::set_last(&ids)?;
            failed.map_or(Ok(()), Err)
        }
        Some("restore") => {
            let ids: Vec<PathBuf> = if arguments.len() == 1 && arguments[0] == "--last" {
                trash::last()?
            } else {
                arguments.into_iter().map(PathBuf::from).collect()
            };
            if ids.is_empty() {
                return Err("nothing to restore".into());
            }
            let mut failed = None;
            for id in ids {
                match trash::restore(&id) {
                    Ok(original) => println!("{}", original.display()),
                    Err(error) => failed = Some(error),
                }
            }
            failed.map_or(Ok(()), Err)
        }
        Some("list") => {
            for entry in trash::list()? {
                println!(
                    "{}\t{}\t{}",
                    entry.deleted,
                    entry.original.display(),
                    entry.id.display()
                );
            }
            Ok(())
        }
        Some("stat") if arguments.is_empty() => stat(),
        Some("empty") => empty(&arguments),
        _ => Err(USAGE.into()),
    }
}

fn stat() -> Result<(), String> {
    let mut rows = Vec::new();
    let mut total = trash::Usage::default();
    for dir in trash::trashes()? {
        if !dir.exists() {
            continue;
        }
        let usage = trash::usage(&dir)?;
        total.items += usage.items;
        total.bytes += usage.bytes;
        rows.push((dir.display().to_string(), usage));
    }
    if rows.len() > 1 {
        rows.push(("total".into(), total));
    }
    let width = rows.iter().map(|(name, _)| name.len()).max().unwrap_or(0);
    for (name, usage) in rows {
        println!(
            "{name:<width$}  {:>6} items  {:>10}",
            usage.items,
            human(usage.bytes)
        );
    }
    Ok(())
}

fn human(bytes: u64) -> String {
    let mut size = bytes as f64;
    for unit in ["B", "KiB", "MiB", "GiB"] {
        if size < 1024.0 {
            return if unit == "B" {
                format!("{bytes} B")
            } else {
                format!("{size:.1} {unit}")
            };
        }
        size /= 1024.0;
    }
    format!("{size:.1} TiB")
}

fn empty(arguments: &[std::ffi::OsString]) -> Result<(), String> {
    let mut older = None;
    let mut yes = false;
    let mut arguments = arguments.iter();
    while let Some(argument) = arguments.next() {
        match argument.to_str() {
            Some("--yes" | "-y") => yes = true,
            Some("--older") => {
                let days: i64 = arguments
                    .next()
                    .and_then(|days| days.to_str()?.parse().ok())
                    .ok_or("--older takes a number of days")?;
                older = Some(days);
            }
            _ => return Err(USAGE.into()),
        }
    }
    // DeletionDate sorts as text, so the cutoff is one too
    let cutoff = older.map(|days| trash::date_ago(days * 86400));
    let entries: Vec<_> = trash::list()?
        .into_iter()
        .filter(|entry| cutoff.as_ref().is_none_or(|cutoff| entry.deleted < *cutoff))
        .collect();
    if entries.is_empty() {
        println!("nothing to delete");
        return Ok(());
    }
    if !yes {
        if !std::io::stdin().is_terminal() {
            return Err("not a terminal; pass --yes to delete without asking".into());
        }
        print!("Delete {} trashed items for good? [y/N] ", entries.len());
        std::io::stdout()
            .flush()
            .map_err(|error| error.to_string())?;
        let mut answer = String::new();
        std::io::stdin()
            .lock()
            .read_line(&mut answer)
            .map_err(|error| error.to_string())?;
        if !answer.trim().eq_ignore_ascii_case("y") {
            return Ok(());
        }
    }
    let mut failed = None;
    for entry in &entries {
        if let Err(error) = trash::purge(entry) {
            failed = Some(error);
        }
    }
    failed.map_or(Ok(()), Err)
}

fn main() {
    if let Err(error) = run() {
        eprintln!("trash: {error}");
        std::process::exit(1);
    }
}
