from pathlib import Path

from config import AppConfig
from layout.layout_detector import LayoutDetector
from layout.structure_parser import StructureParser
from ocr.ocr_engine import OCREngine
from ocr.text_extractor import extract_structured_text
from pipeline.chunking_pipeline import ChunkingPipeline
from utils.file_loader import write_json
from utils.logger import get_logger


class DocumentPipeline:
	def __init__(self, config: AppConfig | None = None):
		self.config = config or AppConfig()
		self.logger = get_logger("document-pipeline")
		self.ocr_engine = OCREngine()
		self.layout_detector = LayoutDetector()
		self.structure_parser = StructureParser()
		self.chunking_pipeline = ChunkingPipeline(
			max_chunk_tokens=self.config.max_chunk_tokens
		)

	def run(self, document_path: Path, source_name: str | None = None) -> dict:
		display_name = source_name or document_path.name
		self.logger.info("Processing %s", display_name)

		if not document_path.exists():
			raise FileNotFoundError(f"Document not found: {document_path}")

		raw_text = self.ocr_engine.extract_text(document_path)

		if not raw_text or not raw_text.strip():
			self.logger.warning("OCR produced no text for %s — skipping chunking", display_name)
			return {"document": display_name, "layout_block_count": 0, "chunk_count": 0, "chunks": []}

		structured_text = extract_structured_text(raw_text)

		# Required order: detect layout first, then chunk from parsed hierarchy.
		layout_blocks = self.layout_detector.detect(structured_text)
		structure = self.structure_parser.parse(layout_blocks)
		chunks = self.chunking_pipeline.run(structure, source_file=display_name)

		if not chunks:
			self.logger.warning("No chunks produced for %s — check layout detection", display_name)

		p = Path(display_name)
		stem = f"{p.stem}_{p.suffix.lstrip('.')}" if p.suffix else p.stem
		write_json(self.config.output_ocr_dir / f"{stem}_ocr.json", structured_text)
		write_json(self.config.output_layout_dir / f"{stem}_layout.json", layout_blocks)
		write_json(self.config.output_structure_dir / f"{stem}_structure.json", structure)
		write_json(self.config.output_chunks_dir / f"{stem}_chunks.json", chunks)

		return {
			"document": display_name,
			"layout_block_count": len(layout_blocks),
			"chunk_count": len(chunks),
			"chunks": chunks,
		}

