import os
import sys

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
)  # noqa: E402
from utils.progress import ProgressTracker, StepProgress  # noqa: E402


def test_format_time():
    assert ProgressTracker._format_time(65) == "0:01:05"
    assert StepProgress._format_time(3600) == "1:00:00"
