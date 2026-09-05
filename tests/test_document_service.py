import pytest
from backend.services.document_service import normalize_text, validate_and_extract, DocumentParsingError

def test_normalize_text():
    raw = "This is a   test\r\n\n\n\nwith extra   spaces and\nPage 1 of 5\nnewlines."
    normalized = normalize_text(raw)
    assert "Page 1 of 5" not in normalized
    assert "   " not in normalized
    assert "This is a test" in normalized

def test_validate_unsupported_format():
    with pytest.raises(DocumentParsingError, match="Unsupported file format"):
        validate_and_extract("contract.xyz", b"sample content")

def test_validate_empty_file():
    with pytest.raises(DocumentParsingError, match="empty"):
        validate_and_extract("contract.pdf", b"")

def test_extract_txt_file():
    content = b"Clause 1: Payment\nThe tenant shall pay monthly rent of INR 20000."
    text, file_type, pages, chars = validate_and_extract("lease.txt", content)
    assert file_type == "txt"
    assert pages >= 1
    assert "Clause 1: Payment" in text
