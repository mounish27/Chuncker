from pathlib import Path

from ocr.ocr_engine import OCREngine


def test_ocr_reads_text_file(tmp_path: Path) -> None:
	file_path = tmp_path / "sample.txt"
	file_path.write_text("hello world", encoding="utf-8")

	engine = OCREngine()
	result = engine.extract_text(file_path)

	assert result == "hello world"

