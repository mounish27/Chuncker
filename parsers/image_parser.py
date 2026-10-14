def parse_image_block(text: str) -> dict:
	return {
		"caption": text,
		"has_caption": bool(text.strip()),
	}

