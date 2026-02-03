import os
import base64
from pdf2image import convert_from_path
from openai import OpenAI
from docx import Document
from io import BytesIO
from dotenv import load_dotenv
import subprocess
import re
load_dotenv()
from PIL import Image
Image.MAX_IMAGE_PIXELS = None

# PDF → IMAGE RENDERER
class PDFToImageRenderer:
    def __init__(self, pdf_path: str, dpi: int = 120):
        self.pdf_path = pdf_path
        self.dpi = dpi
        self.total_pages = self._get_total_pages()

    def _get_total_pages(self) -> int:
        result = subprocess.run(
            ["pdfinfo", self.pdf_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        match = re.search(r"Pages:\s+(\d+)", result.stdout)
        if not match:
            raise RuntimeError("Gagal membaca jumlah halaman PDF")

        return int(match.group(1))

    def render_pages(self, start_page: int = 1, max_pages: int | None = None):
        if start_page > self.total_pages:
            raise ValueError(
                f"start_page ({start_page}) melebihi total halaman PDF ({self.total_pages})"
            )

        first_page = start_page

        if max_pages:
            last_page = min(
                start_page + max_pages - 1,
                self.total_pages
            )
        else:
            last_page = self.total_pages

        print(
            f"📄 Rendering pages {first_page}–{last_page} "
            f"dari total {self.total_pages} halaman"
        )

        return convert_from_path(
            self.pdf_path,
            dpi=self.dpi,
            first_page=first_page,
            last_page=last_page
        )


# OPENAI VISION OCR EXTRACTOR
class OpenAIVisionOCR:
    def __init__(self, model: str = "gpt-4.1"):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = model
    
    def _normalize_image(self, image, max_width=1800):
        # Convert to grayscale (buang warna & ornamen)
        image = image.convert("L")

        # Resize jika terlalu besar
        if image.width > max_width:
            ratio = max_width / image.width
            new_height = int(image.height * ratio)
            image = image.resize((max_width, new_height))

        return image

    def _image_to_base64(self, image) -> str:
        buffer = BytesIO()
        image.save(buffer, format="PNG", optimize=True)
        return base64.b64encode(buffer.getvalue()).decode()

    def extract_catalogue_data(self, image) -> dict:
        image = self._normalize_image(image)
        image_base64 = self._image_to_base64(image)

        prompt = """
Ini adalah SATU halaman katalog produk.

Tugas kamu:
- Lakukan OCR dari gambar
- Abaikan desain, ornamen, background
- Abaikan watermark atau slogan umum
- Fokus pada INTI PRODUK
- Jika teks tidak lengkap, buat deskripsi profesional yang masuk akal

Output HARUS format PERSIS:
Title: ...
Description: ...
"""

        response = self.client.responses.create(
            model=self.model,
            input=[
                {
                    "role": "user",
                    "content": [
                        {"type": "input_text", "text": prompt},
                        {
                            "type": "input_image",
                            "image_url": f"data:image/png;base64,{image_base64}"
                        }
                    ]
                }
            ]
        )

        return self._parse_response(response.output_text)

    def _parse_response(self, text: str) -> dict:
        title = ""
        description_lines = []

        for line in text.splitlines():
            if line.lower().startswith("title"):
                title = line.replace("Title:", "").strip()
            elif line.lower().startswith("description"):
                description_lines.append(line.replace("Description:", "").strip())
            else:
                description_lines.append(line.strip())

        return {
            "title": title,
            "description": " ".join(description_lines)
        }


# WORD DOCUMENT BUILDER
class WordCatalogueBuilder:
    def __init__(self, output_path: str):
        self.doc = Document()
        self.output_path = output_path

    def add_product(self, data: dict):
        if not data["title"]:
            return

        self.doc.add_heading(data["title"], level=2)
        self.doc.add_paragraph(data["description"])

    def save(self):
        self.doc.save(self.output_path)


# MAIN APPLICATION
class CatalogueOCRApp:
    def __init__(
        self,
        pdf_path: str,
        output_docx: str,
        start_page: int = 1,
        max_pages: int | None = None
    ):
        self.renderer = PDFToImageRenderer(pdf_path)
        self.ocr = OpenAIVisionOCR()
        self.writer = WordCatalogueBuilder(output_docx)
        self.start_page = start_page
        self.max_pages = max_pages

    def run(self):
        images = self.renderer.render_pages(
            start_page=self.start_page,
            max_pages=self.max_pages
        )

        for idx, image in enumerate(images):
            page_number = self.start_page + idx
            print(f"🔍 OCR processing page {page_number}...")
            data = self.ocr.extract_catalogue_data(image)
            self.writer.add_product(data)

        self.writer.save()
        print("✅ OCR Catalogue extraction completed!")


# ENTRY POINT
if __name__ == "__main__":
    app = CatalogueOCRApp(
        pdf_path="catalog.pdf",
        output_docx="catalogue_output.docx",
        start_page=1,     # mulai dari halaman berapa
        max_pages=55       # BATAS halaman (WAJIB di production)
    )
    app.run()
