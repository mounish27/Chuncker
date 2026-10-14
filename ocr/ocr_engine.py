import os
from pathlib import Path

from ocr.preprocess import preprocess_document
from utils.file_loader import SUPPORTED_EXTENSIONS, read_text

_OCR_LANG = os.getenv("OCR_LANG", "en")
_OCR_SCALE = float(os.getenv("OCR_SCALE", 1.5))

_IMAGE_EXTENSIONS = SUPPORTED_EXTENSIONS - {".txt", ".pdf"}


class OCREngine:
    def __init__(self):
        self._reader = None

    def _get_reader(self):
        if self._reader is None:
            from paddleocr import PaddleOCR
            # enable_mkldnn=False — fixes PIR-oneDNN bug in PaddlePaddle 3.3.0+ on Windows
            self._reader = PaddleOCR(
                lang=_OCR_LANG,
                enable_mkldnn=False,
                text_recognition_model_name="PP-OCRv5_server_rec",
                use_doc_orientation_classify=False,
                use_doc_unwarping=False,
            )
        return self._reader

    def _extract_texts(self, results) -> str:
        texts = []
        for res in (results or []):
            if isinstance(res, dict) and "rec_texts" in res:
                texts.extend(res["rec_texts"])
        return "\n".join(t for t in texts if t and t.strip())

    def _ocr_array(self, img_array) -> str:
        return self._extract_texts(self._get_reader().predict(img_array))

    def _extract_pdf_page(self, page, doc) -> str:
        import fitz
        import numpy as np

        parts = []

        # 1. Extract embedded text (digital PDF layer)
        embedded = page.get_text().strip()
        if embedded:
            parts.append(embedded)

        # 2. OCR any images embedded in the page (charts, screenshots, image-tables)
        for img_info in page.get_images(full=True):
            xref = img_info[0]
            try:
                base = doc.extract_image(xref)
                img_doc = fitz.open(stream=base["image"], filetype=base["ext"])
                pix = img_doc[0].get_pixmap(colorspace=fitz.csRGB)
                arr = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.h, pix.w, 3)
                ocr_text = self._ocr_array(arr)
                if ocr_text:
                    parts.append(ocr_text)
            except Exception:
                continue

        return "\n".join(parts)

    def _extract_pdf(self, pdf_path: Path) -> str:
        import fitz
        import numpy as np

        doc = fitz.open(str(pdf_path))

        if doc.needs_pass:
            raise ValueError(f"PDF is password-protected and cannot be read: {pdf_path.name}")

        pages: list[str] = []
        for page in doc:
            page_text = self._extract_pdf_page(page, doc)

            # If page has very little text it's a scanned page — render and OCR the whole page
            if len(page_text) < 50:
                pix = page.get_pixmap(
                    matrix=fitz.Matrix(_OCR_SCALE, _OCR_SCALE),
                    colorspace=fitz.csRGB,
                )
                arr = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.h, pix.w, 3)
                page_text = self._ocr_array(arr)

            if page_text:
                pages.append(page_text)

        return "\f".join(pages)

    def extract_text(self, document_path: Path) -> str:
        source = preprocess_document(document_path)
        ext = source.suffix.lower()

        if ext == ".txt":
            return read_text(source)

        if ext in _IMAGE_EXTENSIONS:
            return self._extract_texts(self._get_reader().predict(str(source)))

        if ext == ".pdf":
            return self._extract_pdf(source)

        raise ValueError(f"Unsupported file type '{source.suffix}': {source.name}")
