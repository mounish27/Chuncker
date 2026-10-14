from chunking.chunk_utils import token_count


def build_metadata(source_file: str, section_title: str, block_type: str, text: str) -> dict:
	return {
		"source_file": source_file,
		"section_title": section_title,
		"block_type": block_type,
		"token_count": token_count(text),
	}

