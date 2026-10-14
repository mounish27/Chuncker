import re
from collections import Counter


def _is_tabular(lines: list[str]) -> bool:
	"""Return True if 3+ lines share a consistent column structure (tab or multi-space aligned)."""
	if len(lines) < 3:
		return False
	col_counts = []
	for line in lines:
		cols = [c for c in re.split(r"\t|  +", line.strip()) if c.strip()]
		if len(cols) >= 2:
			col_counts.append(len(cols))
	if len(col_counts) < 3:
		return False
	mode = Counter(col_counts).most_common(1)[0][0]
	return all(abs(c - mode) <= 1 for c in col_counts)


def classify_block(text: str) -> str:
	stripped = text.strip()
	if not stripped:
		return "empty"

	# 1. Markdown headers (### ...)
	if re.match(r"^#{1,6}\s+", stripped):
		return "heading"

	# 2. IEEE Roman Section headers (I. INTRODUCTION, XII. USE CASE...)
	if re.match(r"^[IVXLCDM]+\.\s+[A-Z]", stripped):
		return "heading"

	# 3. IEEE Subsection headers (A. Data Layer)
	if re.match(r"^[A-Z]\.\s+[A-Z]", stripped):
		return "heading"

	# 4. Standard All-Caps Headers or common standalone titles.
	# Single all-caps words under 6 chars are acronyms (NASA, HTTP), not headings.
	if re.match(r"^[A-Z][A-Z\s]{3,}\s*$", stripped):
		words = stripped.split()
		if len(words) > 1 or len(stripped.strip()) >= 6:
			return "heading"

	lines = [l for l in stripped.splitlines() if l.strip()]

	# 5. Pipe-separated table (any line, not just the first)
	if any("|" in line for line in lines):
		return "table"

	# 6. "Table N:" caption prefix on first line
	if lines and re.match(r"^table\s*\d*", lines[0].strip().lower()):
		return "table"

	# 7. Space/tab-aligned table: 3+ lines with consistent column count
	if _is_tabular(lines):
		return "table"

	# "Figure 1:", "Fig. 2", "Figure1" — not "figurative language"
	if re.match(r"^fig(ure)?\.?\s*\d+", stripped, re.IGNORECASE):
		return "figure"

	# "Caption:", "Caption 1:" — not "captioned text" or "caption size"
	if re.match(r"^caption\s*[\d:]", stripped, re.IGNORECASE):
		return "caption"

	return "paragraph"

