import os
import sys
import tempfile

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
)  # noqa: E402
from utils import validation  # noqa: E402


def test_validate_input_file_bad_path():
    valid, msg, ftype = validation.validate_input_file("nonexistent.pdf")
    assert not valid
    assert "does not exist" in msg
    assert ftype is None


def test_validate_page_numbers():
    assert validation.validate_page_numbers([1, 2, 3])
    assert not validation.validate_page_numbers([3, 2, 1])


def test_validate_pdf_integrity_small_file():
    with tempfile.NamedTemporaryFile("wb", delete=False) as f:
        f.write(b"0")
        name = f.name
    try:
        valid, msg = validation.validate_pdf_integrity(name)
        assert not valid
    finally:
        os.remove(name)
