from chunking.hierarchical_chunker import HierarchicalChunker


def test_hierarchical_chunker_returns_chunks() -> None:
	structure = {
		"type": "document",
		"children": [
			{
				"type": "section",
				"title": "Section A",
				"children": [
					{"type": "paragraph", "text": "one two three"},
					{"type": "table", "text": "table content"},
				],
			}
		],
	}

	chunker = HierarchicalChunker(max_chunk_tokens=2)
	chunks = chunker.chunk(structure, source_file="doc.txt")

	assert len(chunks) >= 2
	assert all("metadata" in c for c in chunks)

