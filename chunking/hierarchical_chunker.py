import re
from pathlib import Path

from chunking.chunk_builder import build_chunk
from chunking.chunk_utils import split_by_token_limit, split_table_by_rows


def _doc_prefix(source_file: str) -> str:
	stem = Path(source_file).stem
	return re.sub(r"[^a-zA-Z0-9]+", "_", stem).strip("_")


class HierarchicalChunker:
	def __init__(self, max_chunk_tokens: int = 512):
		self.max_chunk_tokens = max_chunk_tokens

	def chunk(self, structure: dict, source_file: str) -> list[dict]:
		chunks: list[dict] = []
		counter = 1
		prefix = _doc_prefix(source_file)

		for section_index, section in enumerate(structure.get("children", []), start=1):
			section_title = section.get("title", f"Section {section_index}")
			for block_index, block in enumerate(section.get("children", []), start=1):
				block_type = block.get("type", "paragraph")
				text = block.get("text", "").strip()
				if not text:
					continue

				if block_type == "table":
					split_texts = split_table_by_rows(text, self.max_chunk_tokens)
				else:
					split_texts = split_by_token_limit(text, self.max_chunk_tokens)

				for split_idx, split_text in enumerate(split_texts, start=1):
					chunk_id = f"{prefix}__S{section_index}_B{block_index}_C{split_idx}_{counter}"
					chunks.append(
						build_chunk(
							chunk_id=chunk_id,
							text=split_text,
							source_file=source_file,
							section_title=section_title,
							block_type=block_type,
						)
					)
					counter += 1

		return chunks

