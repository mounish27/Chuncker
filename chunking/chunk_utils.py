import math


def token_count(text: str) -> int:
	"""Approximate LLM token count using the 1 token ≈ 4 chars rule."""
	return max(1, math.ceil(len(text) / 4))


def split_by_token_limit(text: str, max_tokens: int) -> list[str]:
	if token_count(text) <= max_tokens:
		return [text]

	max_chars = max_tokens * 4
	words = text.split()
	chunks: list[str] = []
	current: list[str] = []
	current_chars = 0

	for word in words:
		word_len = len(word) + 1  # +1 for the space
		if current_chars + word_len > max_chars and current:
			chunks.append(" ".join(current))
			current = [word]
			current_chars = word_len
		else:
			current.append(word)
			current_chars += word_len

	if current:
		chunks.append(" ".join(current))

	return chunks if chunks else [text]


def split_table_by_rows(text: str, max_tokens: int) -> list[str]:
	lines = [l for l in text.splitlines() if l.strip()]
	if not lines:
		return [text]

	header = lines[0]
	data_rows = lines[1:]

	# If the whole table fits, return as-is
	if token_count(text) <= max_tokens:
		return [text]

	# OCR collapsed the table to one line — no row structure to split on
	if not data_rows:
		return split_by_token_limit(text, max_tokens)

	chunks: list[str] = []
	current_rows: list[str] = []

	for row in data_rows:
		candidate = [header] + current_rows + [row]
		if token_count("\n".join(candidate)) > max_tokens and current_rows:
			chunks.append("\n".join([header] + current_rows))
			current_rows = [row]
		else:
			current_rows.append(row)

	if current_rows:
		chunks.append("\n".join([header] + current_rows))

	# Edge case: a single row exceeds the limit — return it as-is
	return chunks if chunks else [text]

