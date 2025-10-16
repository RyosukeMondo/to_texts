# Quick Start Guide - to_texts Download & Extract Workflow

## Status Check ✅
- ✅ Python environment working
- ✅ Rust text extractor built
- ✅ Text extraction functional (100% success rate)
- ⚠️ Search/Download needs Z-Library credentials

---

## Quick Commands

### 1. Test Everything
```bash
python3 test_download_extract.py
```

**Expected Output:**
```
✓ PASS   Python Environment
✓ PASS   Rust Binary
✓ PASS   Text Extraction
✗ FAIL   Search & Download (Credentials not configured)
```

---

### 2. Extract Existing Books (Works Now!)
```bash
./packages/rust/target/release/text-extractor \
  --target packages/python/zlibrary-downloader/downloads \
  --output ./extracted
```

**Result:** Extracts all EPUB and PDF files to readable text

---

### 3. Download & Extract Full Workflow

#### Setup (One-time)
```bash
# 1. Create .env file
cp packages/python/zlibrary-downloader/.env.example \
   packages/python/zlibrary-downloader/.env

# 2. Edit .env with your credentials
# Option A (Recommended): Add remix cookies
# ZLIBRARY_REMIX_USERID=your_userid
# ZLIBRARY_REMIX_USERKEY=your_userkey

# OR Option B: Add email/password
# ZLIBRARY_EMAIL=your_email@example.com
# ZLIBRARY_PASSWORD=your_password
```

#### Search & Download (Interactive)
```bash
cd packages/python/zlibrary-downloader
./run.sh --tui
```

#### Or Command Line
```bash
./run.sh --title "Python Programming" --download --format epub
```

#### Extract
```bash
./packages/rust/target/release/text-extractor \
  --target packages/python/zlibrary-downloader/downloads \
  --output ./extracted
```

---

## Example Workflow: "Search for 2025 books, download, and extract"

### Step 1: Configure Credentials
```bash
# Add Z-Library credentials to .env
nano packages/python/zlibrary-downloader/.env
```

### Step 2: Search for 2025 Books
```bash
cd packages/python/zlibrary-downloader

# Interactive TUI (Recommended)
./run.sh --tui
# Then: Search for "machine learning" → filter year 2025 → download top 5

# Or CLI mode
for i in {1..5}; do
  ./run.sh --title "python" --download --year-from 2025 --year-to 2025 --page $i
done
```

### Step 3: Extract All Downloaded Books
```bash
cd ..
./packages/rust/target/release/text-extractor \
  --target packages/python/zlibrary-downloader/downloads \
  --output ./extracted_books
```

---

## Troubleshooting

### Issue: "No valid credentials found"
**Solution:**
```bash
cp packages/python/zlibrary-downloader/.env.example \
   packages/python/zlibrary-downloader/.env
# Edit the .env file with your Z-Library credentials
```

### Issue: Text extraction fails
**Solution:** Check if Rust binary is built
```bash
cd packages/rust && cargo build --release
```

---

## Test Results Summary

### Extraction Test (Actual Run)
```
Processing EPUB: The Anxious Generation How_ (Z-Library) (Jonathan Haidt).epub
  → Saved to: The Anxious Generation How_ (Z-Library) (Jonathan Haidt).txt

Processing EPUB: The Let Them Theory A Life-_ (Z-Library) (Mel Robbins, Sawyer Robbins).epub
  → Saved to: The Let Them Theory A Life-_ (Z-Library) (Mel Robbins, Sawyer Robbins).txt

Processing EPUB: Atomic Habits An Easy  Prov_ (Z-Library) (James Clear).epub
  → Saved to: Atomic Habits An Easy  Prov_ (Z-Library) (James Clear).txt

Summary:
  Successfully processed: 3
  Errors: 0
```

### Extracted File Sizes
- Atomic Habits: 459 KB (4,866 lines)
- The Anxious Generation: 802 KB (4,616 lines)
- The Let Them Theory: 479 KB (2,787 lines)
- **Total: 1.8 MB text extracted**

---

## What Each Script Does

### `test_download_extract.py`
Comprehensive test suite that validates:
- Python environment
- Rust binary
- Text extraction
- Search capabilities

### `summarize_books_jp.py`
Generates Japanese language summaries of extracted books:
- Analyzes main themes
- Identifies key arguments
- Extracts practical insights
- Creates markdown report

### `download_and_extract.sh`
Combined workflow script:
1. Downloads from Z-Library
2. Extracts text using Rust CLI
3. Optionally cleans up originals

---

## Performance Benchmarks

| Operation | Time | Files | Success |
|-----------|------|-------|---------|
| Extract 3 EPUBs | ~2 sec | 3 | 100% |
| Total text size | 1.8 MB | 3 | - |
| Avg processing speed | ~1 MB/sec | - | - |

---

## Architecture Overview

```
to_texts Workflow
│
├─ Input: Z-Library
│  ├─ Search with filters (year, language, format)
│  └─ Download EPUB/PDF files
│
├─ Processing: Rust Text Extractor
│  ├─ Parse EPUB/PDF files
│  ├─ Extract text with proper encoding
│  └─ Output clean text files
│
└─ Output: Japanese Summaries (Optional)
   ├─ Use Claude API for NLP
   ├─ Generate Japanese summaries
   └─ Create markdown report
```

---

## Next Steps

1. ✅ Verify extraction is working (DONE - see test results)
2. ⏳ Configure Z-Library credentials
3. ⏳ Download books from 2025
4. ⏳ Extract and verify quality
5. ⏳ Generate Japanese summaries

---

## Files Generated

After testing:
- ✅ `test_download_extract.py` - Test suite
- ✅ `TEST_REPORT.md` - Full test report
- ✅ `QUICK_START_GUIDE.md` - This file
- ✅ `/tmp/to_texts_test_extract/*.txt` - Extracted text samples

---

## For Support

See full details in `TEST_REPORT.md`

