#!/usr/bin/env python3
"""pka2xml.py - giải mã file hoạt động Packet Tracer (.pka) thành XML bằng securedypkt.

Khác với .pkt (chỉ một mạng), file .pka đóng gói một **hoạt động** (Activity):
- có thể chứa NHIỀU bản sao mạng <PACKETTRACER5> (mạng khởi tạo, mạng hiện tại,
  và đôi khi cả mạng đáp án dùng để chấm điểm tự động) thay vì chỉ một;
- có thêm thẻ <ACTIVITY> chứa đề bài (INSTRUCTIONS, dạng HTML) và thời gian
  giới hạn (COUNTDOWNMS);
- thuộc tính VALUE của <ACTIVITY> chứa dữ liệu nhị phân (mã hoá riêng cho phần
  chấm điểm), không phải văn bản XML hợp lệ -> ET.fromstring sẽ báo lỗi
  "not well-formed" nếu không được làm sạch trước.

Việc GIẢI MÃ dùng chung thư viện securedypkt với .pkt (cùng khoá), chỉ khác ở
cách DỰNG TÓM TẮT nói trên.

LƯU Ý: nếu phát hiện nhiều hơn một bản sao mạng, summary liệt kê RIÊNG từng bản
và đánh số thứ tự — một trong số đó có thể là mạng đáp án. Cân nhắc trước khi
chia sẻ summary cho sinh viên.

Cài thư viện:   pip install securedypkt
Ví dụ:
    python pka2xml.py bai1.pka                    # ra bai1.xml
    python pka2xml.py bai1.pka --summary          # ra bai1.xml + bai1.summary.txt
    python pka2xml.py bai1.pka --summary --configs
    python pka2xml.py ./labs -o ./out --summary   # cả thư mục
File XML rất lớn (vài MB), nên khi gửi cho Claude hãy gửi file .summary.txt.
"""
import argparse
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

try:
    import securedypkt
except ImportError:
    sys.exit("Thiếu thư viện. Chạy: pip install securedypkt")

EXT = ".pka"

# Byte điều khiển không hợp lệ trong XML 1.0 (giữ lại tab \x09, newline \x0a, CR \x0d)
_INVALID_XML_CHARS = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f]")
_TAG_RE = re.compile(r"<[^>]+>")


def find_files(inputs):
    """Trả về danh sách file .pka từ các đường dẫn (file hoặc thư mục)."""
    files = []
    for item in inputs:
        p = Path(item)
        if p.is_dir():
            files += sorted(f for f in p.rglob("*") if f.suffix.lower() == EXT)
        elif p.is_file():
            files.append(p)
        else:
            print(f"[bỏ qua] không tìm thấy: {p}")
    return files


def sanitize_xml(xml_bytes):
    """Loại bỏ byte điều khiển không hợp lệ (ví dụ trong <ACTIVITY VALUE="...">)
    để ET.fromstring không báo lỗi "not well-formed". Không đổi nội dung văn bản
    còn lại, chỉ ảnh hưởng tới đúng cụm dữ liệu nhị phân bị cắt bỏ."""
    text = xml_bytes.decode("utf-8", errors="replace")
    return _INVALID_XML_CHARS.sub("", text)


def strip_html(html):
    """Bỏ thẻ HTML trong đề bài (ACTIVITY/INSTRUCTIONS/PAGE), gộp khoảng trắng thừa."""
    text = _TAG_RE.sub(" ", html)
    text = (text.replace("&nbsp;", " ").replace("&amp;", "&")
                .replace("&lt;", "<").replace("&gt;", ">").replace("&quot;", '"'))
    return re.sub(r"[ \t]+", " ", text).strip()


def summarize_network(pt, with_configs=False):
    """Tóm tắt một bản sao <PACKETTRACER5>: thiết bị, IP, link, (running-config).
    Giống phần lõi của build_summary trong pkt2xml.py."""
    lines = []
    names = {}
    for dev in pt.iter("DEVICE"):
        eng = dev.find("ENGINE")
        if eng is None:
            continue
        name = eng.findtext("NAME")
        names[eng.findtext("SAVE_REF_ID")] = name
        typ = eng.find("TYPE")
        model = typ.get("model") if typ is not None else None
        lines.append(f"   == {name}" + (f" ({model})" if model else ""))
        for port in eng.iter("PORT"):
            ip, mask = port.findtext("IP"), port.findtext("SUBNET")
            if ip:
                lines.append(f"      port: {ip} / {mask}")
            for a in port.iter("IPV6_ADDRESS"):
                lines.append(f"      ipv6: {a.findtext('ADDRESS')}/{a.findtext('PREFIX')}")
        lan = eng.findtext(".//LAN_IP_ADDRESS")
        if lan and lan != "0.0.0.0":
            lines.append(f"      lan_ip: {lan} / {eng.findtext('.//LAN_SUBNET_MASK')}")
        for tag in ("GATEWAY", "IPV6_GATEWAY", "DNS_SERVER"):
            for g in eng.iter(tag):
                if g.text and g.text.strip():
                    lines.append(f"      {tag.lower()}: {g.text.strip()}")
        if with_configs:
            rc = eng.find("RUNNINGCONFIG")
            if rc is not None:
                cfg = [ln.text for ln in rc.findall("LINE") if ln.text and ln.text.strip() != "!"]
                if cfg:
                    lines.append("      --- running-config ---")
                    lines += [f"      {c}" for c in cfg]

    link_lines = []
    for link in pt.iter("LINK"):
        cable = link.find("CABLE")
        if cable is None:
            continue
        a, b = cable.findtext("FROM"), cable.findtext("TO")
        ports = [p.text for p in cable.findall("PORT")][:2]
        if len(ports) < 2:
            continue
        link_lines.append(f"   {names.get(a, a)} [{ports[0]}] <-> {names.get(b, b)} [{ports[1]}]"
                           f"  ({link.findtext('TYPE')})")
    if link_lines:
        lines.append("   -- LINKS --")
        lines += link_lines
    if not lines:
        lines.append("   (mạng rỗng)")
    return lines


def build_summary(xml_bytes, with_configs=False):
    """Tóm tắt: version, giới hạn thời gian, đề bài, rồi từng bản sao mạng."""
    root = ET.fromstring(sanitize_xml(xml_bytes))
    lines = [f"Packet Tracer version: {root.findtext('VERSION')}", ""]

    act = root.find("ACTIVITY")
    if act is not None:
        ms = act.get("COUNTDOWNMS")
        if ms and ms.isdigit() and int(ms) > 0:
            lines.append(f"Giới hạn thời gian: {int(ms) // 60000} phút "
                          f"(enabled={act.get('ENABLED')})")
        page = act.find("INSTRUCTIONS/PAGE")
        if page is not None and page.text:
            text = strip_html(page.text)
            if text:
                lines += ["", "== ĐỀ BÀI (INSTRUCTIONS) =="]
                lines.append(text[:4000] + ("..." if len(text) > 4000 else ""))
        lines.append("")

    networks = root.findall("PACKETTRACER5")
    if len(networks) > 1:
        lines.append(
            f"[!] File có {len(networks)} bản sao mạng (có thể gồm: mạng khởi tạo, "
            "mạng hiện tại, và mạng đáp án dùng để chấm điểm tự động). Liệt kê "
            "riêng từng bản bên dưới — cân nhắc trước khi chia sẻ cho sinh viên, "
            "vì một trong số đó có thể là đáp án.")
        lines.append("")

    for i, pt in enumerate(networks, 1):
        label = f"MẠNG #{i}/{len(networks)}" if len(networks) > 1 else "MẠNG"
        lines.append(f"-- {label} --")
        lines += summarize_network(pt, with_configs)
        lines.append("")

    return "\n".join(lines) + "\n"


def convert(path, outdir, summary, configs):
    out_base = (outdir or path.parent) / path.stem
    xml_bytes = securedypkt.decrypt_file(str(path))
    out_base.with_suffix(".xml").write_bytes(xml_bytes)
    print(f"[ok] {path.name} -> {out_base.name}.xml ({len(xml_bytes) // 1024} KB)")
    if summary:
        text = build_summary(xml_bytes, configs)
        Path(f"{out_base}.summary.txt").write_text(text, encoding="utf-8")
        print(f"[ok] {path.name} -> {out_base.name}.summary.txt")


def main():
    ap = argparse.ArgumentParser(description="Giải mã .pka (hoạt động Packet Tracer) thành XML")
    ap.add_argument("inputs", nargs="+", help="file hoặc thư mục")
    ap.add_argument("-o", "--outdir", help="thư mục xuất (mặc định: cạnh file gốc)")
    ap.add_argument("-s", "--summary", action="store_true", help="xuất thêm file tóm tắt .summary.txt")
    ap.add_argument("-c", "--configs", action="store_true", help="kèm running-config trong file tóm tắt")
    args = ap.parse_args()

    outdir = Path(args.outdir) if args.outdir else None
    if outdir:
        outdir.mkdir(parents=True, exist_ok=True)

    failed = 0
    for f in find_files(args.inputs):
        try:
            convert(f, outdir, args.summary, args.configs)
        except Exception as e:  # file lỗi hoặc phiên bản chưa hỗ trợ
            failed += 1
            print(f"[lỗi] {f.name}: {type(e).__name__}: {e}")
    if failed:
        print(f"{failed} file thất bại.")
        sys.exit(1)


if __name__ == "__main__":
    main()