"""Sinh dữ liệu cho trang web (index.html) từ labs/**, cheatsheets/*.md.

Hosting tĩnh không liệt kê được thư mục và mở index.html bằng file:// thì fetch bị chặn,
nên dữ liệu được nhúng thẳng vào index.html, giữa hai dòng đánh dấu LAB-DATA.
Chạy lại sau mỗi lần thêm hoặc sửa bài:

    python tools/build_web.py            # ghi lại khối dữ liệu trong index.html
    python tools/build_web.py --check    # chỉ kiểm tra index.html có khớp không (thoát 1 nếu lệch)
"""
import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INDEX = ROOT / "index.html"
START, END = "<!--LAB-DATA-START-->", "<!--LAB-DATA-END-->"


def read(p):
    return p.read_text(encoding="utf-8").replace("\r\n", "\n")


def chapter_of(text, fallback=""):
    m = re.search(r"Chương\s+(\d+)", text)
    return m.group(1) if m else fallback


def split_first_sentence(text):
    """'Dựng A3: ... VLAN 1. Đặt tên ...' -> ('Dựng A3: ... VLAN 1.', 'Đặt tên ...')."""
    m = re.match(r"(.+?[.!?])(?:\s+(.*))?$", text, re.S)
    if m:
        return m.group(1).strip(), (m.group(2) or "").strip()
    return text.strip(), ""


def parse_steps(de, n_steps):
    """Lấy tiêu đề từng bước từ de.md. Ba kiểu viết đang có trong các bài:
    '## Bước N - tiêu đề', '**Bước N.** nội dung', và danh sách '1. nội dung' dưới mục có chữ 'bước'."""
    found = {}
    for m in re.finditer(r"^##\s+Bước\s+(\d+)\s*[-:–]\s*(.+)$", de, re.M):
        found[int(m.group(1))] = (m.group(2).strip(), "")
    if not found:
        for m in re.finditer(r"^\*\*Bước\s+(\d+)\.\*\*\s*(.+)$", de, re.M):
            found[int(m.group(1))] = split_first_sentence(m.group(2))
    if not found:
        in_sec = False
        for line in de.split("\n"):
            if line.startswith("## "):
                in_sec = "bước" in line.lower()
                continue
            m = re.match(r"(\d+)\.\s+(.+)$", line)
            if in_sec and m:
                found[int(m.group(1))] = split_first_sentence(m.group(2))
    return [
        {"n": n, "title": found.get(n, (f"Bước {n}", ""))[0], "detail": found.get(n, ("", ""))[1]}
        for n in range(1, n_steps + 1)
    ]


def build_lab(checks_path):
    spec = json.loads(read(checks_path))
    d = checks_path.parent
    de = read(d / "de.md")
    n_steps = spec.get("steps", 1)
    steps = parse_steps(de, n_steps)
    for s in steps:
        active = [c for c in spec["checks"] if c.get("from", 1) <= s["n"] <= c.get("to", 99)]
        devs = []
        for c in active:
            for k in ("device", "a", "b"):
                if k in c:
                    name = str(c[k]).split(":")[0]
                    if name not in devs:
                        devs.append(name)
        s["checks"] = len(active)
        s["devices"] = devs
    h1 = re.match(r"#\s+(.+)", de)
    title = h1.group(1).strip() if h1 else spec.get("title", d.name)
    rel = d.relative_to(ROOT / "labs").as_posix()
    return {
        "id": rel,
        "chapter": re.sub(r"\D", "", rel.split("/")[0]),
        "title": title,
        "short": re.sub(r"^Chương\s+\d+\s*[-–]\s*", "", title),
        "steps": steps,
        "de": de,
    }


def build_cheatsheet(p):
    text = read(p)
    h1 = re.match(r"#\s+(.+)", text)
    title = h1.group(1).strip() if h1 else p.stem
    parts = re.split(r"^##\s+", text, flags=re.M)
    intro = re.sub(r"^#\s+.+\n", "", parts[0]).strip()
    sections = []
    for part in parts[1:]:
        head, _, body = part.partition("\n")
        sections.append({"h": re.sub(r"^\d+\.\s*", "", head.strip()), "md": body.strip()})
    return {
        "id": p.stem,
        "chapter": chapter_of(title),
        "title": title,
        "short": re.sub(r"^Cheatsheet:\s*", "", title),
        "intro": intro,
        "sections": sections,
    }


def build_pitfalls(p):
    chapter = re.sub(r"\D", "", p.parent.name)
    items = []
    for m in re.finditer(r"^\d+\.\s+\*\*(.+?)\*\*\s*(.*)$", read(p), re.M):
        items.append({"chapter": chapter, "title": m.group(1).strip(), "md": m.group(2).strip()})
    return items


def build():
    labs = [build_lab(p) for p in sorted(ROOT.glob("labs/**/checks.json"))]
    sheets = [build_cheatsheet(p) for p in sorted(ROOT.glob("cheatsheets/*.md"))]
    pitfalls = []
    for p in sorted(ROOT.glob("labs/chuong-*/loi-hay-gap.md")):
        pitfalls += build_pitfalls(p)
    return {"labs": labs, "cheatsheets": sheets, "pitfalls": pitfalls}


def render_block(data):
    raw = json.dumps(data, ensure_ascii=False, indent=1).replace("</", "<\\/")
    return f'{START}\n<script id="lab-data" type="application/json">\n{raw}\n</script>\n{END}'


def main():
    ap = argparse.ArgumentParser(description="Nhúng dữ liệu bài lab vào index.html")
    ap.add_argument("--check", action="store_true", help="chỉ kiểm tra index.html có khớp dữ liệu hiện tại")
    a = ap.parse_args()
    html = read(INDEX)
    pat = re.compile(re.escape(START) + r".*?" + re.escape(END), re.S)
    if not pat.search(html):
        sys.exit(f"index.html thiếu cặp {START} ... {END}")
    new = pat.sub(lambda _: render_block(build()), html, count=1)
    if a.check:
        if new != html:
            sys.exit("index.html chưa khớp dữ liệu: chạy python tools/build_web.py")
        print("ok: index.html khớp dữ liệu")
        return
    if new != html:
        INDEX.write_text(new, encoding="utf-8", newline="\n")
        print("Đã cập nhật index.html")
    else:
        print("index.html đã khớp, không đổi gì")


if __name__ == "__main__":
    main()
