import os
import json
import time
from PyPDF2 import PdfReader
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer, LTTextLine, LTChar
import fitz  # PyMuPDF
import multiprocessing

# Font size to heading level mapping
STANDARD_HEADING_SIZES = {
    "H1": 24,
    "H2": 18,
    "H3": 14.04,
    "H4": 12,
    "H5": 9.96
}
THRESHOLD = 2.0
HEADING_TIMEOUT = 20  # seconds

# --- Title Extraction using PyMuPDF ---
def extract_title_pymupdf(pdf_path):
    try:
        doc = fitz.open(pdf_path)
        title_spans = []

        for i in range(min(3, len(doc))):  # Check first 3 pages
            page = doc[i]
            blocks = page.get_text("dict")["blocks"]
            spans = []

            for b in blocks:
                for l in b.get("lines", []):
                    for span in l.get("spans", []):
                        text = span["text"].strip()
                        if text:
                            spans.append({
                                "text": text,
                                "size": span["size"],
                                "y": span["bbox"][1],
                                "x": span["bbox"][0]
                            })

            if not spans:
                continue

            # Find the max font size
            max_size = max(spans, key=lambda x: x["size"])["size"]

            # Get all spans with that font size (allow tiny tolerance)
            title_spans = [s for s in spans if abs(s["size"] - max_size) < 0.5]

            if title_spans:
                # Sort by vertical (y), then horizontal (x)
                title_spans.sort(key=lambda s: (s["y"], s["x"]))
                title_text = " ".join(s["text"] for s in title_spans)
                return title_text

    except Exception as e:
        print(f"❌ Error extracting title with PyMuPDF: {e}")

    return None


# --- Assign heading level based on font size ---
def assign_html_heading_level(font_size):
    closest_level = None
    smallest_diff = float('inf')
    for level, std_size in STANDARD_HEADING_SIZES.items():
        diff = abs(font_size - std_size)
        if diff < smallest_diff:
            smallest_diff = diff
            closest_level = level
    return closest_level if smallest_diff <= THRESHOLD else None

# --- Headings Extraction Function for multiprocessing ---
def extract_headings_worker(pdf_path, min_text_length, return_dict):
    try:
        outline = []
        for page_num, layout in enumerate(extract_pages(pdf_path), start=1):
            for element in layout:
                if isinstance(element, LTTextContainer):
                    for tl in element:
                        font_size = None
                        if hasattr(tl, "_objs"):
                            for char in tl._objs:
                                if isinstance(char, LTChar):
                                    font_size = char.size
                                    break
                        if font_size is not None:
                            text = tl.get_text().strip()
                            if len(text) >= min_text_length:
                                level = assign_html_heading_level(font_size)
                                if level:
                                    outline.append({
                                        "level": level,
                                        "text": text,
                                        "page": page_num
                                    })
        return_dict["outline"] = outline
    except Exception as e:
        return_dict["error"] = f"❌ Error in extract_headings_worker: {e}"

# --- Extract Headings with Timeout ---
def extract_headings_pdfminer_with_timeout(pdf_path, min_text_length=3):
    manager = multiprocessing.Manager()
    return_dict = manager.dict()
    p = multiprocessing.Process(target=extract_headings_worker, args=(pdf_path, min_text_length, return_dict))
    p.start()
    p.join(HEADING_TIMEOUT)

    if p.is_alive():
        p.terminate()
        p.join()
        print(f"⚠️ Heading extraction timed out after {HEADING_TIMEOUT} seconds.")
        return []
    if "error" in return_dict:
        print(return_dict["error"])
        return []
    return return_dict.get("outline", [])

# --- Fallback Title if all else fails ---
def fallback_title(pdf_path):
    try:
        reader = PdfReader(pdf_path)
        meta_title = reader.metadata.title
        if meta_title:
            return meta_title.strip()
    except Exception:
        pass
    return os.path.splitext(os.path.basename(pdf_path))[0]

# --- Main function to process each PDF ---
def process_pdf(pdf_path, output_path):
    print(f"\n📄 Processing: {pdf_path}")
    start_time = time.time()

    # Extract title
    title_start = time.time()
    title = extract_title_pymupdf(pdf_path)
    if not title:
        title = fallback_title(pdf_path)
    title_end = time.time()
    print(f"⏱️ Title extraction time: {title_end - title_start:.2f} seconds")

    # Extract headings (with timeout)
    heading_start = time.time()
    outline = extract_headings_pdfminer_with_timeout(pdf_path)
    heading_end = time.time()
    print(f"⏱️ Headings extraction time: {heading_end - heading_start:.2f} seconds")

    # Save output
    output = {
        "title": title,
        "outline": outline
    }
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    total_time = time.time() - start_time
    print(f"✅ Title: {title}")
    print(f"📝 Output saved to: {output_path}")
    print(f"🕒 Total processing time: {total_time:.2f} seconds")
