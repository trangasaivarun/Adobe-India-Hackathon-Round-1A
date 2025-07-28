
# 📄 PDF Outliner – Adobe Challenge Round 1A

This project is built for **Adobe's Round 1A: Connecting the Dots Challenge**, where the task is to process PDFs and extract a structured outline including the **title**, **headings (H1, H2, H3)**, and their **page numbers**. The output is saved in a structured JSON format.

---

## 📁 Directory Structure

```
adobe_1a/
│
├── Dockerfile                  # Docker configuration for the project
├── final_pdf_processor.py     # Core logic to extract titles and outlines from PDF
├── requirements.txt           # Python dependencies
├── run.py                     # Main script to process input PDFs
├── input_pdfs/                # Folder containing input PDF files
└── output_jsons/              # Output folder with extracted outline JSON files
```

---

## ⚙️ Features

- **Title Extraction**: Identifies the most prominent title using font size and visual position.
- **Outline Extraction**: Detects headings (H1, H2, H3) based on font size analysis across all pages.
- **Multi-page Parsing**: Scans all pages to ensure complete outline extraction.
- **JSON Output**: Stores the structured result in a clean JSON format.
- **Dockerized**: Fully containerized for platform-independent execution.

---

## 🐳 Docker Setup (Recommended)

### 🔧 Build the Docker Image

```bash
docker build -t pdf-outliner:v1 .
```

### ▶️ Run the Container

```bash
docker run --rm \
  -v "$(pwd)/input_pdfs:/app/input_pdfs" \
  -v "$(pwd)/output_jsons:/app/output_jsons" \
  pdf-outliner:v1
```

This will process all PDFs inside `input_pdfs/` and save the output `.json` files inside `output_jsons/`.

---

## 🧠 How It Works

### `final_pdf_processor.py`

- Opens each PDF using `PyMuPDF` (`fitz`).
- Collects all font sizes to identify heading hierarchies.
- **Title Detection**:
  - Uses the largest font size.
  - Selects the top-most text block on the first page.
- **Heading Classification**:
  - Based on frequency and relative size, it classifies text blocks into H1, H2, or H3.
  - Tracks their page number and exact text content.
- Outputs results in the form:
```json
{
  "title": "Document Title",
  "outline": [
    {
      "level": "H1",
      "text": "Section 1",
      "page": 1
    },
    {
      "level": "H2",
      "text": "Subsection 1.1",
      "page": 2
    }
  ]
}
```

### `run.py`

- Scans the `input_pdfs` directory.
- For each PDF file:
  - Invokes `process_pdf()` from `final_pdf_processor.py`.
  - Saves output JSON with the same base name.

---

## 📦 Requirements

Dependencies are defined in `requirements.txt`:

```text
PyMuPDF
PyPDF2
pdfminer.six
```

Install manually (for non-Docker use):

```bash
pip install -r requirements.txt
```

---

## 💡 Tips

- Use high-quality PDFs with searchable text (non-scanned).
- If headings are not detected, adjust the font size threshold logic in `final_pdf_processor.py`.

---

## 🧪 Sample Input/Output

- Sample PDFs are placed inside `input_pdfs/`.
- Output for each file will be stored in `output_jsons/` with `.json` extension.

---

## 🛠 Future Improvements

- Add multilingual PDF support.
- Train ML model to identify sections semantically.
- GUI/REST API for PDF uploads.
