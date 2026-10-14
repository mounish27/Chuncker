import json
from pathlib import Path
from typing import Any

SUPPORTED_EXTENSIONS: frozenset[str] = frozenset({
	".txt", ".pdf", ".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".tif"
})


def list_documents(input_dir: Path) -> list[Path]:
	return [
		p
		for p in input_dir.iterdir()
		if p.is_file() and p.suffix.lower() in SUPPORTED_EXTENSIONS
	]


def read_text(path: Path) -> str:
	try:
		return path.read_text(encoding="utf-8")
	except UnicodeDecodeError:
		return path.read_text(encoding="latin-1")


def write_json(path: Path, payload: Any) -> None:
	path.parent.mkdir(parents=True, exist_ok=True)
	path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

