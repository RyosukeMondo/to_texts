use anyhow::{Context, Result};
use clap::Parser;
use std::fs;
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
    fs::create_dir_all(&args.output)
        .context(format!("Failed to create output directory: {}", args.output.display()))?;

    println!("Searching for PDF and EPUB files in: {}", args.target.display());
    println!("Output directory: {}", args.output.display());
    println!();

    let mut processed_count = 0;
    let mut error_count = 0;

    // Walk through the directory recursively
    for entry in WalkDir::new(&args.target)
        .follow_links(true)
        .into_iter()
        .filter_map(|e| e.ok())
    {
        let path = entry.path();

        if !path.is_file() {
            continue;
        }

        let extension = path.extension().and_then(|s| s.to_str()).unwrap_or("");

        match extension.to_lowercase().as_str() {
            "pdf" => {
                println!("Processing PDF: {}", path.display());
                match extract_pdf_text(path, &args.output) {
                    Ok(output_path) => {
                        println!("  -> Saved to: {}", output_path.display());
                        processed_count += 1;
                    }
                    Err(e) => {
                        eprintln!("  -> Error: {}", e);
                        error_count += 1;
                    }
                }
            }
            "epub" => {
                println!("Processing EPUB: {}", path.display());
                match extract_epub_text(path, &args.output) {
                    Ok(output_path) => {
                        println!("  -> Saved to: {}", output_path.display());
                        processed_count += 1;
                    }
                    Err(e) => {
                        eprintln!("  -> Error: {}", e);
                        error_count += 1;
                    }
                }
            }
            _ => continue,
        }
    }

    println!();
    println!("Summary:");
    println!("  Successfully processed: {}", processed_count);
    println!("  Errors: {}", error_count);

    Ok(())
}

fn extract_pdf_text(pdf_path: &Path, output_dir: &Path) -> Result<PathBuf> {
    use pdf::file::FileOptions;
    use pdf::content::Op;

    let file = FileOptions::cached()
        .open(pdf_path)
        .context(format!("Failed to open PDF: {}", pdf_path.display()))?;

    let resolver = file.resolver();
    let mut text = String::new();

    // Extract text from each page
    for page_num in 0..file.num_pages() {
        text.push_str(&format!("\n\n--- Page {} ---\n\n", page_num + 1));

        match file.get_page(page_num) {
            Ok(page) => {
                if let Some(ref contents) = page.contents {
                    match contents.operations(&resolver) {
                        Ok(ops) => {
                            for op in ops {
                                match op {
                                    Op::TextDraw { text: text_draw } => {
                                        let string = String::from_utf8_lossy(&text_draw.data);
                                        text.push_str(&string);
                                        text.push(' ');
                                    }
                                    Op::TextDrawAdjusted { array } => {
                                        for item in array.iter() {
                                            match item {
                                                pdf::content::TextDrawAdjusted::Text(pdf_string) => {
                                                    let string = String::from_utf8_lossy(&pdf_string.data);
                                                    text.push_str(&string);
                                                }
                                                pdf::content::TextDrawAdjusted::Spacing(_) => {
                                                    text.push(' ');
                                                }
                                            }
                                        }
                                    }
                                    _ => {}
                                }
                            }
                        }
                        Err(e) => {
                            eprintln!("  Warning: Failed to read operations on page {}: {}", page_num + 1, e);
                        }
                    }
                }
            }
            Err(e) => {
                eprintln!("  Warning: Failed to read page {}: {}", page_num + 1, e);
            }
        }
    }

    // Generate output file path
    let output_path = generate_output_path(pdf_path, output_dir, "txt")?;

    // Write extracted text to file
    fs::write(&output_path, text)
        .context(format!("Failed to write output file: {}", output_path.display()))?;

    Ok(output_path)
}

fn extract_epub_text(epub_path: &Path, output_dir: &Path) -> Result<PathBuf> {
    let mut doc = epub::doc::EpubDoc::new(epub_path)
        .context(format!("Failed to open EPUB: {}", epub_path.display()))?;

    let mut text = String::new();

    // Extract metadata
    if let Some(title) = doc.mdata("title") {
        text.push_str("Title: ");
        text.push_str(&title);
        text.push_str("\n");
    }
    if let Some(creator) = doc.mdata("creator") {
        text.push_str("Author: ");
        text.push_str(&creator);
        text.push_str("\n");
    }
    text.push_str("\n");
    text.push_str("=" .repeat(80).as_str());
    text.push_str("\n\n");

    // Extract text from all resources
    let resources = doc.resources.clone();
    for (path, (mime_type, _)) in resources.iter() {
        // Only process HTML/XHTML content
        if mime_type.starts_with("application/xhtml") || mime_type.starts_with("text/html") {
            if let Some((content, _)) = doc.get_resource_str(path) {
                // Basic HTML tag stripping (simple approach)
                let cleaned = strip_html_tags(&content);
                text.push_str(&cleaned);
                text.push_str("\n\n");
            }
        }
    }

    // Generate output file path
    let output_path = generate_output_path(epub_path, output_dir, "txt")?;

    // Write extracted text to file
    fs::write(&output_path, text)
        .context(format!("Failed to write output file: {}", output_path.display()))?;

    Ok(output_path)
}

fn strip_html_tags(html: &str) -> String {
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

            // Check if entering script or style tag
            let tag_lower = tag_name.to_lowercase();
            if tag_lower == "script" || tag_lower == "style" {
                in_script_style = true;
            } else if tag_lower == "/script" || tag_lower == "/style" {
                in_script_style = false;
            }

            tag_name.clear();
        } else if in_tag {
            if tag_name.len() < 20 {  // Limit tag name length
                tag_name.push(ch);
            }
        } else if !in_script_style {
            result.push(ch);
        }
    }

    // Clean up whitespace
    result
        .split('\n')
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
