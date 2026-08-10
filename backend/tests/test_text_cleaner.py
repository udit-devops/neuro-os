from app.rag.text_cleaner import clean_text


def test_normalizes_line_endings():
    assert clean_text("a\r\nb\r\nc") == "a\nb\nc"
    assert clean_text("a\rb") == "a\nb"


def test_removes_control_characters():
    text = "a\x00b\x07c"
    assert clean_text(text) == "abc"


def test_collapses_excessive_blank_lines():
    assert clean_text("a\n\n\n\nb") == "a\n\nb"


def test_strips_trailing_spaces_and_outer_whitespace():
    assert clean_text("  hello world  \n") == "hello world"


def test_preserves_single_blank_lines():
    assert clean_text("para one\n\npara two") == "para one\n\npara two"


def test_preserves_tabs():
    assert clean_text("a\tb") == "a\tb"