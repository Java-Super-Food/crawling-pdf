# OCR Catalogue Extractor (PDF → Structured Text → PDF)

This project is a **production-ready OCR pipeline** designed to extract **meaningful textual content** from **catalogue-style PDF files** using **OpenAI Vision (OCR + reasoning)**.

It is optimized for **text understanding**, not pixel fidelity, and is suitable for:

- Product catalogues  
- Marketing brochures  
- Design-heavy PDFs  
- Scanned documents  
- Print-ready layouts (InDesign, posters, flyers)

---

## 🚀 Features

- 📄 **PDF page rendering with page limits**
- 👁️ **OCR using OpenAI Vision (image-based, not text-layer)**
- 🧠 **Semantic extraction** (understands content, not just raw text)
- ⚡ **Optimized rendering** (low DPI, grayscale, resized images)
- 🧱 **OOP architecture** (clean, modular, extensible)
- 📑 **Direct PDF output** (no Word dependency)
- 💰 **Cost-safe** (page limit enforced)
- 🐧 **WSL / Linux friendly**

---

## 🧠 Processing Pipeline
```
PDF
└── Render pages as images (text-first, low DPI)
└── Normalize image (grayscale + resize)
└── OpenAI Vision OCR + reasoning
└── Structured data (Title + Description)
└── Output PDF
```

---


---

## 📦 Requirements

### System Dependencies (Linux / WSL)

These are **OS-level dependencies** and must be installed **outside Python venv**.

```bash
sudo apt update
sudo apt install -y \
  python3 \
  python3-pip \
  python3-venv \
  poppler-utils

# Verify Poppler installation:
pdfinfo -v
```

### Python Dependencies

**Installed inside a virtual environment (venv):**
- openai
- pdf2image
- pillow
- python-dotenv
- reportlab

## 🔑 **Environment Variables**

Create a .env file in the project root:
```
OPENAI_API_KEY=your_openai_api_key_here
```

⚠️ Never commit .env to version control.

## **🛠️ Installation & Setup (Step-by-Step)**
1. Clone or Prepare Project Directory
```bash
mkdir ocr-catalogue
cd ocr-catalogue

# Place your script file, for example:
ocr_catalog.py
```
2. Create Python Virtual Environment
``` bash
python3 -m venv venv
# Activate it:
source venv/bin/activate
# You should see:
(venv) user@machine:~/ocr-catalogue$
```
3. Install Python Dependencies
``` bash
pip install -r requirements.txt
# or
pip install \
  openai \
  pdf2image \
  pillow \
  python-dotenv \
  reportlab

```

**Running the OCR Pipeline**
```
python3 ocr_catalog.py
```