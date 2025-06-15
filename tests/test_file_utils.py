import os
import sys
import tempfile

sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..")),
)
from utils import file_utils  # noqa: E402


def test_normalize_and_basename():
    path = file_utils.normalize_path("foo/bar.txt")
    assert file_utils.get_basename(path) == "bar"
    assert file_utils.get_basename(path, with_extension=True) == "bar.txt"


def test_ensure_dir():
    with tempfile.TemporaryDirectory() as tmpdir:
        new_dir = os.path.join(tmpdir, "sub")
        file_utils.ensure_dir(new_dir)
        assert os.path.isdir(new_dir)


def test_create_project_structure():
    with tempfile.TemporaryDirectory() as tmpdir:
        result = file_utils.create_project_structure(tmpdir, "Book")
        for key in ["project", "images", "text", "chapters", "combined"]:
            assert os.path.isdir(result[key])


def test_create_zip_archive():
    with tempfile.TemporaryDirectory() as tmpdir:
        f1 = os.path.join(tmpdir, "a.txt")
        with open(f1, "w") as f:
            f.write("hi")
        zip_path = os.path.join(tmpdir, "out.zip")
        file_utils.create_zip_archive(tmpdir, zip_path)
        assert os.path.isfile(zip_path)
