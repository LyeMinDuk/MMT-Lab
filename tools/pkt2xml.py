#!/usr/bin/env python3
"""pkt2xml.py - giải mã file Packet Tracer (.pkt/.pka) thành XML bằng securedypkt.

Cài thư viện:   pip install securedypkt
Ví dụ:
    python pkt2xml.py bt1.pkt                    # ra bt1.xml
    python pkt2xml.py bt1.pkt --summary          # ra bt1.xml + bt1.summary.txt
    python pkt2xml.py bt1.pkt --summary --configs
    python pkt2xml.py ./labs -o ./out --summary  # cả thư mục
File XML rất lớn (cỡ 1MB), nên khi gửi cho Claude hãy gửi file .summary.txt.
"""
import argparse
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

try:
    import securedypkt
except ImportError:
    sys.exit("Thiếu thư viện. Chạy: pip install securedypkt")

EXTS = {".pkt", ".pka"}


def find_files(inputs):
    """Trả về danh sách file .pkt/.pka từ các đường dẫn (file hoặc thư mục)."""
    files = []
    for item in inputs:
        p = Path(item)
        if p.is_dir():
            files += sorted(f for f in p.rglob("*") if f.suffix.lower() in EXTS)
        elif p.is_file():
            files.append(p)
        else:
            print(f"[bỏ qua] không tìm thấy: {p}")
    return files


def build_summary(xml_bytes, with_configs=False):
    """Tóm tắt: version, thiết bị, IP, gateway, danh sách link (và running-config)."""
    root = ET.fromstring(xml_bytes)
    lines = [f"Packet Tracer version: {root.findtext('VERSION')}", ""]
    names = {}  # save-ref-id -> tên thiết bị

    for dev in root.iter("DEVICE"):
        eng = dev.find("ENGINE")
        if eng is None:
            continue
        name = eng.findtext("NAME")
        names[eng.findtext("SAVE_REF_ID")] = name
        lines.append(f"== {name} ({eng.find('TYPE').get('model')})")
        for port in eng.iter("PORT"):
            ip, mask = port.findtext("IP"), port.findtext("SUBNET")
            if ip:
                lines.append(f"   port: {ip} / {mask}")
            for a in port.iter("IPV6_ADDRESS"):
                lines.append(f"   ipv6: {a.findtext('ADDRESS')}/{a.findtext('PREFIX')}")
        lan = eng.findtext(".//LAN_IP_ADDRESS")
        if lan and lan != "0.0.0.0":
            lines.append(f"   lan_ip: {lan} / {eng.findtext('.//LAN_SUBNET_MASK')}")
        for tag in ("GATEWAY", "IPV6_GATEWAY", "DNS_SERVER"):
            for g in eng.iter(tag):
                if g.text and g.text.strip():
                    lines.append(f"   {tag.lower()}: {g.text.strip()}")
        if with_configs:
            rc = eng.find("RUNNINGCONFIG")
            if rc is not None:
                lines.append("   --- running-config ---")
                for ln in rc.findall("LINE"):
                    if ln.text and ln.text.strip() != "!":
                        lines.append("   " + ln.text)

    lines += ["", "== LINKS"]
    for link in root.iter("LINK"):
        cable = link.find("CABLE")
        if cable is None:
            continue
        a, b = cable.findtext("FROM"), cable.findtext("TO")
        pa, pb = [p.text for p in cable.findall("PORT")][:2]
        lines.append(f"   {names.get(a, a)} [{pa}] <-> {names.get(b, b)} [{pb}]"
                     f"  ({link.findtext('TYPE')})")
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
    ap = argparse.ArgumentParser(description="Giải mã .pkt/.pka thành XML")
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
        print(f"{failed} file thất bại. Với .pka có thể thử pka2xml thay thế.")
        sys.exit(1)


if __name__ == "__main__":
    main()
