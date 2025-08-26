import pytest
from unittest.mock import MagicMock, patch
from api.services.ocr import extract_text_from_pdf
from api.services.ocr import extract_sections, build_topic_draft_from_text
from api.model.topic import TopicDraft


def make_fake_pdf_page(text):
    page = MagicMock()
    textpage = MagicMock()
    textpage.extractText.return_value = text
    page.get_textpage.return_value = textpage
    return page


@patch("api.services.ocr.pymupdf")
def test_extract_text_from_pdf_single_page(mock_pymupdf):
    fake_page = make_fake_pdf_page("Hello World\n")
    mock_doc = [fake_page]
    mock_pymupdf.open.return_value = mock_doc

    result = extract_text_from_pdf(b"fake_pdf_bytes")
    assert result == "Hello World\n"


@patch("api.services.ocr.pymupdf")
def test_extract_text_from_pdf_multiple_pages(mock_pymupdf):
    fake_page1 = make_fake_pdf_page("Page 1\n")
    fake_page2 = make_fake_pdf_page("Page 2\n")
    mock_doc = [fake_page1, fake_page2]
    mock_pymupdf.open.return_value = mock_doc

    result = extract_text_from_pdf(b"fake_pdf_bytes")
    assert result == "Page 1\nPage 2\n"


@patch("api.services.ocr.pymupdf")
def test_extract_text_from_pdf_empty_pdf(mock_pymupdf):
    mock_doc = []
    mock_pymupdf.open.return_value = mock_doc

    result = extract_text_from_pdf(b"fake_pdf_bytes")
    assert result == ""


@patch("api.services.ocr.pymupdf")
def test_extract_text_from_pdf_raises_exception(mock_pymupdf):
    mock_pymupdf.open.side_effect = Exception("Failed to open PDF")
    with pytest.raises(Exception):
        extract_text_from_pdf(b"bad_pdf_bytes")


def test_extract_sections_basic():
    text = """Title: My Story
Premise: Something happens
Environment: A forest
Exposition: The hero arrives
First Action: Runs away
"""
    sections = extract_sections(text)
    assert sections["Title"] == "My Story"
    assert sections["Premise"] == "Something happens"
    assert sections["Environment"] == "A forest"
    assert sections["Exposition"] == "The hero arrives"
    assert sections["First Action"] == "Runs away"


def test_extract_sections_missing_headers():
    text = """My Story
Something happens
A forest
"""
    sections = extract_sections(text)
    assert sections["Title"].startswith("My Story")
    assert "Premise" not in sections


def test_extract_sections_headers_with_colon():
    text = """Title: My Story
Premise: Something happens
Tone: Serious
"""
    sections = extract_sections(text)
    assert sections["Title"] == "My Story"
    assert sections["Premise"] == "Something happens"
    assert sections["Tone"] == "Serious"


def test_extract_sections_headers_without_colon():
    text = """Title
My Story
Premise
Something happens
"""
    sections = extract_sections(text)
    assert sections["Title"] == "My Story"
    assert sections["Premise"] == "Something happens"


def test_extract_sections_case_insensitive():
    text = """title: My Story
premise: Something happens
"""
    sections = extract_sections(text)
    assert sections["Title"] == "My Story"
    assert sections["Premise"] == "Something happens"


def test_extract_sections_extra_lines():
    text = """Title: My Story

Premise: Something happens

Environment: A forest

Extra line not in header
"""
    sections = extract_sections(text)
    assert "Extra line not in header" in sections["Environment"]


def test_build_topic_draft_from_text_basic():
    text = """Title: My Story
Premise: Something happens
Environment: A forest
"""
    draft = build_topic_draft_from_text(text)
    assert isinstance(draft, TopicDraft)
    assert draft.title == "My Story"
    assert (
        draft.open_prompt is not None
        and "Something happens" in draft.open_prompt
        and "A forest" in draft.open_prompt
    )


def test_build_topic_draft_from_text_no_title():
    text = """Premise: Something happens
Environment: A forest
"""
    draft = build_topic_draft_from_text(text)
    assert draft.title == "Untitled"
    assert draft.open_prompt is not None and "Something happens" in draft.open_prompt


def test_build_topic_draft_from_text_empty():
    text = ""
    draft = build_topic_draft_from_text(text)
    assert draft.title == "Untitled"
    assert draft.open_prompt == ""
