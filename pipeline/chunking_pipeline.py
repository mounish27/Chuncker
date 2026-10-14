from chunking.hierarchical_chunker import HierarchicalChunker


class ChunkingPipeline:
	def __init__(self, max_chunk_tokens: int = 180):
		self.chunker = HierarchicalChunker(max_chunk_tokens=max_chunk_tokens)

	def run(self, structure: dict, source_file: str) -> list[dict]:
		return self.chunker.chunk(structure, source_file=source_file)

