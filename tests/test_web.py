"""Kiểm tra phần web: dữ liệu nhúng trong index.html khớp labs/ + cheatsheets/, mỗi bước đều có tiêu đề."""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import build_web  # noqa: E402


def embedded():
    html = (ROOT / "index.html").read_text(encoding="utf-8")
    m = re.search(r'<script id="lab-data" type="application/json">\n(.*?)\n</script>', html, re.S)
    assert m, "index.html thiếu khối lab-data"
    return json.loads(m.group(1).replace("<\\/", "</"))


def test_in_sync():
    assert embedded() == build_web.build(), "index.html chưa khớp dữ liệu: chạy python tools/build_web.py"


def test_steps_parsed():
    for lab in build_web.build()["labs"]:
        spec = json.loads((ROOT / "labs" / lab["id"] / "checks.json").read_text(encoding="utf-8"))
        assert len(lab["steps"]) == spec["steps"], lab["id"]
        for s in lab["steps"]:
            assert not s["title"].startswith("Bước "), (lab["id"], s["n"], "không tách được tiêu đề từ de.md")
            assert s["checks"] > 0, (lab["id"], s["n"], "bước không có tiêu chí chấm nào")


def test_content_found():
    d = build_web.build()
    assert d["cheatsheets"] and all(c["sections"] for c in d["cheatsheets"])
    assert d["pitfalls"]


if __name__ == "__main__":
    test_in_sync()
    test_steps_parsed()
    test_content_found()
    print("ok test_web")
