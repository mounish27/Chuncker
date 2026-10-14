import argparse
from pathlib import Path

from pipeline.document_pipeline import DocumentPipeline


def main() -> None:
	parser = argparse.ArgumentParser(description="OCR + Layout + Hierarchical Chunking")
	parser.add_argument("--input", required=True, help="Path to input document/image/text")
	args = parser.parse_args()

	input_path = Path(args.input)
	if not input_path.exists():
		raise FileNotFoundError(f"Input file not found: {input_path}")

	pipeline = DocumentPipeline()
	result = pipeline.run(input_path)
	print(
		f"Processed {result['document']} | layout blocks={result['layout_block_count']} | chunks={result['chunk_count']}"
	)


if __name__ == "__main__":
	main()

