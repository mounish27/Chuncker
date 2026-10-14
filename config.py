import os
from dataclasses import dataclass
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

@dataclass(frozen=True)
class AppConfig:
	base_dir: Path = Path(__file__).parent
	input_documents_dir: Path = base_dir / "input" / "documents"
	input_images_dir: Path = base_dir / "input" / "images"
	output_ocr_dir: Path = base_dir / "output" / "ocr_text"
	output_chunks_dir: Path = base_dir / "output" / "chunks"
	output_layout_dir: Path = base_dir / "output" / "layouts"
	output_structure_dir: Path = base_dir / "output" / "structures"
	max_chunk_tokens: int = int(os.getenv("MAX_CHUNK_TOKENS", 512))
	ocr_lang: str = os.getenv("OCR_LANG", "en")
	ocr_scale: float = float(os.getenv("OCR_SCALE", 1.5))

