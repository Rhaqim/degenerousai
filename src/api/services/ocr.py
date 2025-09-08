import io
import re
from typing import Dict

import pymupdf
import docx2txt

from model.topic import TopicDraft


async def parse_ocr(file_bytes: bytes, file_type: str) -> TopicDraft:
    """
    Parses uploaded file content and returns a TopicDraft.
    Uses OCR for PDFs and images, plain text for .txt, and docx2txt for Word docs.
    """
    try:
        if file_type == "pdf":
            text = extract_text_from_pdf(file_bytes)
        elif file_type == "txt":
            text = file_bytes.decode("utf-8", errors="ignore")
        elif file_type in ["doc", "docx"]:
            text = extract_text_from_docx(file_bytes)
        else:
            raise ValueError("Unsupported file type")

        topic_draft = build_topic_draft_from_text(text)

        return topic_draft

    except Exception as e:
        raise RuntimeError(f"Failed to parse OCR content: {str(e)}")


def extract_text_from_pdf(file_bytes: bytes) -> str:
    with io.BytesIO(file_bytes) as f:
        doc = pymupdf.open(stream=f, filetype="pdf")
        text = ""
        for page in doc:  # iterate the document pages
            text += page.get_textpage().extractText()  # get plain text
        return text


def extract_text_from_docx(file_bytes: bytes) -> str:
    with io.BytesIO(file_bytes) as f:
        return docx2txt.process(f)


SECTION_HEADERS = [
    "Title",
    "Premise",
    "Environment",
    "Exposition",
    "First Action",
    "Main Character",
    "Side Characters",
    "Relationships",
    "Winning Scenarios",
    "Losing Scenarios",
    "Key Events",
    "Tone",
    "Additional Data",
]


def extract_sections(text: str) -> Dict[str, str]:
    """
    Parses text into sections based on known headers.
    Returns a dictionary of section name -> content.
    """
    sections = {}
    current_key = "Title"
    sections[current_key] = []

    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue

        header_match = next(
            (
                h
                for h in SECTION_HEADERS
                if re.fullmatch(h + r":?", line, re.IGNORECASE)
            ),
            None,
        )
        if header_match:
            current_key = header_match
            sections[current_key] = []
        else:
            sections.setdefault(current_key, []).append(line)

    return {k: "\n".join(v).strip() for k, v in sections.items()}


def build_topic_draft_from_text(text: str) -> TopicDraft:
    sections = extract_sections(text)

    title = sections.get("Title", "Untitled")
    open_prompt = "\n".join(
        v for k, v in sections.items() if k not in ["Title"]
    ).strip()

    return TopicDraft(
        title=title, story_data=None, open_prompt=open_prompt, table_prompt=None
    )
