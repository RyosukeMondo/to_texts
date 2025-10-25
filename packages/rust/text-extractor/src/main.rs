use anyhow::{Context, Result};
use clap::Parser;
use std::fs;
use std::panic;
use std::path::{Path, PathBuf};
use walkdir::WalkDir;

#[derive(Parser, Debug)]
#[command(name = "to_texts")]
#[command(about = "Extract text from PDF and EPUB files recursively", long_about = None)]
struct Args {
    /// Target path to search recursively for PDF or EPUB files
    #[arg(short, long)]
    target: PathBuf,

    /// Output path to save extracted texts
    #[arg(short, long)]
    output: PathBuf,
}

fn main() -> Result<()> {
    let args = Args::parse();

    // Validate target path exists
    if !args.target.exists() {
        anyhow::bail!("Target path does not exist: {}", args.target.display());
    }

    // Create output directory if it doesn't exist
    fs::create_dir_all(&args.output).context(format!(
        "Failed to create output directory: {}",
        args.output.display()
    ))?;

    println!(
        "Searching for PDF and EPUB files in: {}",
        args.target.display()
    );
    println!("Output directory: {}", args.output.display());
    println!();

    let (processed_count, error_count) = process_directory(&args.target, &args.output)?;

    print_summary(processed_count, error_count);

    Ok(())
}

fn process_directory(target: &Path, output: &Path) -> Result<(usize, usize)> {
    let mut processed_count = 0;
    let mut error_count = 0;

    // Walk through the directory recursively
    for entry in WalkDir::new(target)
        .follow_links(true)
        .into_iter()
        .filter_map(|e| e.ok())
    {
        let path = entry.path();

        if !path.is_file() {
            continue;
        }

        if let Some(extension) = path.extension().and_then(|s| s.to_str()) {
            match extension.to_lowercase().as_str() {
                "pdf" | "epub" => {
                    if process_file(path, output, extension) {
                        processed_count += 1;
                    } else {
                        error_count += 1;
                    }
                }
                _ => continue,
            }
        }
    }

    Ok((processed_count, error_count))
}

fn process_file(path: &Path, output: &Path, extension: &str) -> bool {
    let file_type = extension.to_lowercase();
    println!(
        "Processing {}: {}",
        file_type.to_uppercase(),
        path.display()
    );

    let result = match file_type.as_str() {
        "pdf" => extract_pdf_text(path, output),
        "epub" => extract_epub_text(path, output),
        _ => return false,
    };

    match result {
        Ok(output_path) => {
            println!("  -> Saved to: {}", output_path.display());
            true
        }
        Err(e) => {
            eprintln!("  -> Error: {}", e);
            false
        }
    }
}

fn print_summary(processed_count: usize, error_count: usize) {
    println!();
    println!("Summary:");
    println!("  Successfully processed: {}", processed_count);
    println!("  Errors: {}", error_count);
}

fn extract_pdf_text(pdf_path: &Path, output_dir: &Path) -> Result<PathBuf> {
    // Extract text using pdf-extract which properly handles encodings
    // Catch panics from the pdf-extract library
    let text = panic::catch_unwind(|| {
        pdf_extract::extract_text(pdf_path)
    })
    .map_err(|_| anyhow::anyhow!("PDF extraction panicked (likely unsupported PDF feature)"))
    .and_then(|r| r.context(format!(
        "Failed to extract text from PDF: {}",
        pdf_path.display()
    )))?;

    // Generate output file path
    let output_path = generate_output_path(pdf_path, output_dir, "txt")?;

    // Write extracted text to file
    fs::write(&output_path, text).context(format!(
        "Failed to write output file: {}",
        output_path.display()
    ))?;

    Ok(output_path)
}

fn extract_epub_text(epub_path: &Path, output_dir: &Path) -> Result<PathBuf> {
    let mut doc = epub::doc::EpubDoc::new(epub_path)
        .context(format!("Failed to open EPUB: {}", epub_path.display()))?;

    let mut text = String::new();

    // Extract metadata
    append_metadata(&doc, &mut text);

    // Extract text from all resources
    extract_resources(&mut doc, &mut text);

    // Generate output file path and write
    let output_path = generate_output_path(epub_path, output_dir, "txt")?;
    fs::write(&output_path, text).context(format!(
        "Failed to write output file: {}",
        output_path.display()
    ))?;

    Ok(output_path)
}

fn append_metadata(doc: &epub::doc::EpubDoc<std::io::BufReader<std::fs::File>>, text: &mut String) {
    if let Some(title) = doc.mdata("title") {
        text.push_str("Title: ");
        text.push_str(&title);
        text.push('\n');
    }
    if let Some(creator) = doc.mdata("creator") {
        text.push_str("Author: ");
        text.push_str(&creator);
        text.push('\n');
    }
    text.push('\n');
    text.push_str("=".repeat(80).as_str());
    text.push_str("\n\n");
}

fn extract_resources(
    doc: &mut epub::doc::EpubDoc<std::io::BufReader<std::fs::File>>,
    text: &mut String,
) {
    let resources = doc.resources.clone();

    for (resource_id, (file_path, mime_type)) in resources.iter() {
        if is_html_content(mime_type, &file_path.to_string_lossy()) {
            if let Some((content, _)) = doc.get_resource_str(resource_id) {
                let cleaned = strip_html_tags(&content);
                text.push_str(&cleaned);
                text.push_str("\n\n");
            }
        }
    }
}

fn is_html_content(mime_type: &str, path_str: &str) -> bool {
    mime_type.starts_with("application/xhtml")
        || mime_type.starts_with("text/html")
        || path_str.ends_with(".xhtml")
        || path_str.ends_with(".html")
}

fn strip_html_tags(html: &str) -> String {
    let raw_text = extract_text_from_html(html);
    clean_whitespace(&raw_text)
}

fn extract_text_from_html(html: &str) -> String {
    let mut result = String::new();
    let mut in_tag = false;
    let mut in_script_style = false;
    let mut tag_name = String::new();

    for ch in html.chars() {
        if ch == '<' {
            in_tag = true;
            tag_name.clear();
        } else if ch == '>' {
            in_tag = false;
            in_script_style = update_script_style_state(&tag_name, in_script_style);
            tag_name.clear();
        } else if in_tag {
            if tag_name.len() < 20 {
                // Limit tag name length
                tag_name.push(ch);
            }
        } else if !in_script_style {
            result.push(ch);
        }
    }

    result
}

fn update_script_style_state(tag_name: &str, current_state: bool) -> bool {
    let tag_lower = tag_name.to_lowercase();
    if tag_lower == "script" || tag_lower == "style" {
        true
    } else if tag_lower == "/script" || tag_lower == "/style" {
        false
    } else {
        current_state
    }
}

fn clean_whitespace(text: &str) -> String {
    text.split('\n')
        .map(|line| line.trim())
        .filter(|line| !line.is_empty())
        .collect::<Vec<_>>()
        .join("\n")
}

fn generate_output_path(input_path: &Path, output_dir: &Path, extension: &str) -> Result<PathBuf> {
    let file_stem = input_path
        .file_stem()
        .context("Failed to get file stem")?
        .to_string_lossy();

    let output_filename = format!("{}.{}", file_stem, extension);
    Ok(output_dir.join(output_filename))
}
