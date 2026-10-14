import re

_HEADER_PATTERN = re.compile(
	r"^(?:"
	r"[IVXLCDM]+\.\s+[A-Z]"       # IEEE Roman: I. INTRODUCTION
	r"|[A-Z]\.\s+[A-Z]"            # IEEE subsection: A. Overview
	r"|#{1,6}\s+"                   # Markdown: ## Title
	r"|[A-Z][A-Z\s]{3,}\s*$"       # All-caps standalone: BACKGROUND
	r")"
)


def _is_header(line: str) -> bool:
	return bool(_HEADER_PATTERN.match(line.strip()))


def extract_structured_text(raw_text: str) -> dict:
	paragraphs: list[str] = []
	page_map: list[int] = []
	current_paragraph: list[str] = []
	current_page = 1

	def flush():
		if current_paragraph:
			paragraphs.append(" ".join(current_paragraph))
			page_map.append(current_page)
			current_paragraph.clear()

	for line in raw_text.splitlines():
		if "\f" in line:
			flush()
			current_page += 1
			continue

		stripped = line.strip()

		if not stripped:
			flush()
			continue

		if _is_header(stripped):
			flush()
			paragraphs.append(stripped)
			page_map.append(current_page)
		else:
			current_paragraph.append(stripped)

	flush()

	pairs = [(p, pg) for p, pg in zip(paragraphs, page_map) if p]
	return {
		"raw_text": raw_text,
		"paragraphs": [p for p, _ in pairs],
		"page_map": [pg for _, pg in pairs],
	}

