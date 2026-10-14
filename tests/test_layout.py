from layout.layout_detector import LayoutDetector
from layout.structure_parser import StructureParser


def test_layout_and_structure_parser() -> None:
	structured_text = {
		"paragraphs": [
			"INTRODUCTION",
			"This is a paragraph.",
			"Table 1: Data Summary",
		]
	}

	detector = LayoutDetector()
	parser = StructureParser()

	blocks = detector.detect(structured_text)
	structure = parser.parse(blocks)

	assert len(blocks) == 3
	assert structure["type"] == "document"
	assert len(structure["children"]) >= 1

