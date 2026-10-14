from utils.logger import get_logger

_logger = get_logger("structure-parser")


class StructureParser:
	def parse(self, blocks: list[dict]) -> dict:
		document = {"type": "document", "children": []}
		current_section = None

		for block in blocks:
			if block["type"] == "heading":
				title = block["text"]
				if len(title) > 120:
					_logger.warning("Heading truncated in section_title (was %d chars): %.60s…", len(title), title)
					title = title[:120]
				current_section = {
					"type": "section",
					"title": title,
					"children": [block],
				}
				document["children"].append(current_section)
				continue

			if current_section is None:
				_logger.warning(
					"Content found before the first heading — grouping under 'Preamble'. "
					"Block text: %.60s", block.get("text", "")
				)
				current_section = {
					"type": "section",
					"title": "Preamble",
					"children": [],
				}
				document["children"].append(current_section)

			current_section["children"].append(block)

		return document

