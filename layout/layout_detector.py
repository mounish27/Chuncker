from layout.block_classifier import classify_block


class LayoutDetector:
	def detect(self, structured_text: dict) -> list[dict]:
		paragraphs = structured_text.get("paragraphs", [])
		page_map = structured_text.get("page_map", [])
		blocks: list[dict] = []
		for idx, paragraph in enumerate(paragraphs, start=1):
			block_type = classify_block(paragraph)
			if block_type == "empty":
				continue
			blocks.append(
				{
					"id": idx,
					"type": block_type,
					"text": paragraph,
					"page": page_map[idx - 1] if idx - 1 < len(page_map) else 1,
				}
			)
		return blocks

