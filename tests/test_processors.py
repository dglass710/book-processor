import builtins
import os
import sys
from unittest import mock

sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..")),
)

import pytest  # noqa: E402


@pytest.fixture(autouse=True, scope="module")
def mock_deps():
    orig_pypdf2 = sys.modules.get("PyPDF2")
    orig_fitz = sys.modules.get("fitz")
    sys.modules["PyPDF2"] = mock.MagicMock()
    sys.modules["fitz"] = mock.MagicMock()
    yield
    if orig_pypdf2 is not None:
        sys.modules["PyPDF2"] = orig_pypdf2
    else:
        sys.modules.pop("PyPDF2", None)
    if orig_fitz is not None:
        sys.modules["fitz"] = orig_fitz
    else:
        sys.modules.pop("fitz", None)


def test_converter_check_dependencies():
    with mock.patch(
        "utils.file_utils.check_command_exists",
        return_value=False,
    ):
        from processors.converter import FormatConverter

        conv = FormatConverter()
        success, _ = conv.check_dependencies()
        assert not success


def test_extractor_check_dependencies():
    import processors.extractor as extractor

    sys.modules.pop("fitz", None)
    orig_import = builtins.__import__

    def fake_import(name, globals=None, locals=None, fromlist=(), level=0):
        if name == "fitz":
            raise ImportError
        if name == "PyPDF2":
            return mock.MagicMock()
        return orig_import(name, globals, locals, fromlist, level)

    with mock.patch("builtins.__import__", side_effect=fake_import):
        ext = extractor.PDFExtractor()
        success, _ = ext.check_dependencies()

    assert not success


def test_ocr_check_dependencies():
    with mock.patch("processors.ocr.check_command_exists", return_value=False):
        from processors.ocr import OCRProcessor

        ocr = OCRProcessor()
        success, _ = ocr.check_dependencies()
        assert not success
