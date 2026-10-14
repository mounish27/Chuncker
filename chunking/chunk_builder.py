from chunking.metadata_builder import build_metadata


def build_chunk(
	chunk_id: str,
	text: str,
	source_file: str,
	section_title: str,
	block_type: str,
) -> dict:
	return {
		"chunk_id": chunk_id,
		"text": text,
		"metadata": build_metadata(source_file, section_title, block_type, text),
	}

