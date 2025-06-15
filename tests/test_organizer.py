import os
import sys

sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..")),
)
from processors.organizer import ChapterOrganizer  # noqa: E402,E501
from processors.organizer import CombinedChapterOrganizer  # noqa: E402


def test_parse_chapter_locations():
    org = ChapterOrganizer()
    chapters = org.parse_chapter_locations(
        [1, 10],
        ["Intro", "Main"],
        max_page=20,
    )
    assert len(chapters) == 3  # includes back matter
    assert chapters[0]["title"] == "Intro"


def test_process_chapter_and_combined(tmp_path):
    org = ChapterOrganizer()
    chapter = {"number": 1, "title": "Intro", "start_page": 1, "end_page": 2}
    text_dir = tmp_path / "text"
    os.makedirs(text_dir)
    for i in range(1, 3):
        with open(text_dir / f"page-{i:03d}.txt", "w") as f:
            f.write(f"Page {i}")
    output_dir = tmp_path / "chapters"
    success, msg, path, count = org.process_chapter(chapter, str(text_dir), str(output_dir))
    assert success
    assert count > 0
    comb = CombinedChapterOrganizer()
    groups = [{"file": "01", "chapters": [1], "desc": "Intro"}]
    c_out = tmp_path / "combined"
    success, msg, c_path = comb.create_combined_file(groups[0], [chapter], str(output_dir), str(c_out))
    assert success
    assert os.path.isfile(c_path)
