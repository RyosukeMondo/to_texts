use epub::doc::EpubDoc;
use std::path::Path;

fn main() {
    let path = Path::new("/home/rmondo/repos/to_texts/packages/python/zlibrary-downloader/downloads/The Let Them Theory A Life-_ (Z-Library) (Mel Robbins, Sawyer Robbins).epub");
    
    let mut doc = EpubDoc::new(&path).expect("Failed to open EPUB");
    
    println!("Title: {:?}", doc.mdata("title"));
    println!("Author: {:?}", doc.mdata("creator"));
    println!("\nResources:");
    
    for (path, (mime_type, _)) in doc.resources.iter().take(10) {
        println!("  {} -> {}", path, mime_type);
    }
    
    println!("\nTotal resources: {}", doc.resources.len());
}
