import re


def clean_text(text: str) -> str:
    """Normalize whitespace while preserving paragraph and markdown structure."""
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = "".join(char for char in text if char == "\n" or char == "\t" or char.isprintable())
    lines = [line.rstrip() for line in text.split("\n")]
    text = "\n".join(lines)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()
