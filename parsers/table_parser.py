def parse_table_block(text: str) -> dict:
	rows = [row.strip() for row in text.split("\n") if row.strip()]
	return {
		"row_count": len(rows),
		"raw": text,
	}

