import importlib.util
import pathlib

import pytest

COMMON_MODULE_PATH = pathlib.Path(__file__).resolve().parents[3] / "src" / "lib" / "common.py"
spec = importlib.util.spec_from_file_location("signalhire_common", COMMON_MODULE_PATH)
common = importlib.util.module_from_spec(spec)
assert spec.loader is not None  # for type checkers
spec.loader.exec_module(common)

normalize_path_for_display = common.normalize_path_for_display


@pytest.mark.parametrize(
    "raw_path,expected",
    [
        ("/home/vanman2025/output.csv", "/home/vanman2025/output.csv"),
        ("\\\\wsl.localhost\\Ubuntu\\home\\user\\file.csv", "/home/user/file.csv"),
        ("//wsl.localhost/Ubuntu/home/user/file.csv", "/home/user/file.csv"),
        ("C:/Users/example/Downloads/report.csv", "/mnt/c/Users/example/Downloads/report.csv"),
        ("", ""),
    ],
)
def test_normalize_path_for_display(raw_path, expected):
    assert normalize_path_for_display(raw_path) == expected


def test_normalize_path_for_display_handles_none():
    assert normalize_path_for_display(None) == ""
