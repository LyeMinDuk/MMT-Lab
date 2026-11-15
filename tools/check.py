#!/usr/bin/env python3
"""check.py - chấm bài Packet Tracer offline (đọc file .pkt/.pka/.xml).

Ví dụ:
    python tools/check.py bai.pkt --lab labs/chuong-2/thuc-hanh-03-bai-nop
    python tools/check.py bai.pkt --lab labs/chuong-2/thuc-hanh-02-kich-ban --step 6
    python tools/check.py bai.pkt --dump          # in những gì script đọc được từ file

Script chỉ chấm CẤU HÌNH (VLAN, cổng, trunk, IP, cáp...). Ping thật vẫn phải tự thử
trong Packet Tracer. Thông báo chỉ nêu "yêu cầu" và "thực tế", không đưa sẵn lệnh sửa.
"""
import argparse
import ipaddress
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ALL_VLANS = set(range(1, 1006))


# ---------- tiện ích chuẩn hoá ----------
def norm_port(name):
    """FastEthernet0/1, fa0/1, Fa 0/1 -> Fa0/1 ; GigabitEthernet0/1, Gig0/1 -> Gi0/1."""
    n = re.sub(r"\s+", "", name or "")
    n = re.sub(r"(?i)^gigabitethernet", "Gi", n)
    n = re.sub(r"(?i)^gig(?=\d)", "Gi", n)
    n = re.sub(r"(?i)^fastethernet", "Fa", n)
    n = re.sub(r"(?i)^fa(?=\d)", "Fa", n)
    n = re.sub(r"(?i)^gi(?=\d)", "Gi", n)
    return n


def expand_ports(spec):
    """'Fa0/6-10' -> Fa0/6..Fa0/10 ; 'Fa0/1,Fa0/3' -> 2 cổng."""
    out = []
    for part in spec.split(","):
        part = norm_port(part.strip())
        m = re.fullmatch(r"([A-Za-z]+\d+/)(\d+)-(\d+)", part)
        if m:
            out += [f"{m[1]}{i}" for i in range(int(m[2]), int(m[3]) + 1)]
        elif part:
            out.append(part)
    return out


def parse_vlans(text):
    """'2-4,7' -> {2,3,4,7}"""
    s = set()
    for part in text.replace(" ", "").split(","):
        if "-" in part:
            a, b = part.split("-")
            s |= set(range(int(a), int(b) + 1))
        elif part:
            s.add(int(part))
    return s


def fmt_vlans(s):
    """{2,3,4,7} -> '2-4,7'"""
    nums, out = sorted(s), []
    i = 0
    while i < len(nums):
        j = i
        while j + 1 < len(nums) and nums[j + 1] == nums[j] + 1:
            j += 1
        out.append(str(nums[i]) if i == j else f"{nums[i]}-{nums[j]}")
        i = j + 1
    return ",".join(out) or "(rỗng)"


# ---------- đọc file thành model ----------
def load_xml(path):
    p = Path(path)
    if p.suffix.lower() == ".xml":
        return p.read_bytes()
    try:
        import securedypkt
    except ImportError:
        sys.exit("Thiếu thư viện. Chạy: pip install securedypkt")
    return securedypkt.decrypt_file(str(p))


def parse_config(lines, dev):
    """Đọc running-config: hostname, enable secret, cấu hình từng cổng."""
    cur = None
    for raw in lines:
        s = raw.strip()
        if raw.startswith("interface "):
            cur = norm_port(raw.split(None, 1)[1])
            dev["ports"][cur] = []
        elif raw.startswith(" ") and cur:
            dev["ports"][cur].append(s)
        else:
            cur = None
            if s.startswith("hostname "):
                dev["hostname"] = s.split(None, 1)[1]
            elif s.startswith("enable secret"):
                dev["enable_secret"] = True


def parse_device(eng):
    t = eng.find("TYPE")
    dev = {"model": t.get("model") if t is not None else None, "vlans": {},
           "hostname": None, "enable_secret": False, "ports": {},
           "ipv4": [], "ipv6": []}
    for v in eng.iterfind("VLANS/VLAN"):
        dev["vlans"][int(v.get("number"))] = v.get("name")
    rc = eng.find("RUNNINGCONFIG")
    if rc is not None:
        parse_config([ln.text or "" for ln in rc.findall("LINE")], dev)
    for port in eng.iter("PORT"):
        ip, mask = port.findtext("IP"), port.findtext("SUBNET")
        if ip:
            dev["ipv4"].append((ip, mask))
        for a in port.iter("IPV6_ADDRESS"):
            dev["ipv6"].append((a.findtext("ADDRESS"), int(a.findtext("PREFIX") or 0)))
    return dev


def build_model(xml_bytes):
    root = ET.fromstring(xml_bytes)
    devices, refs = {}, {}
    for d in root.iter("DEVICE"):
        eng = d.find("ENGINE")
        if eng is None:
            continue
        name = eng.findtext("NAME")
        refs[eng.findtext("SAVE_REF_ID")] = name
        devices[name] = parse_device(eng)
    links = set()
    for link in root.iter("LINK"):
        c = link.find("CABLE")
        if c is None:
            continue
        p = [norm_port(x.text) for x in c.findall("PORT")][:2]
        if len(p) == 2:
            links.add(frozenset([(refs.get(c.findtext("FROM")), p[0]),
                                 (refs.get(c.findtext("TO")), p[1])]))
    return {"version": root.findtext("VERSION"), "devices": devices, "links": links}


def port_info(dev, port):
    """Suy ra mode / access vlan / trunk allowed / shutdown của cổng từ các dòng cấu hình."""
    info = {"mode": None, "access": 1, "allowed": set(ALL_VLANS), "native": 1,
            "shutdown": False, "lines": dev["ports"].get(port, [])}
    for s in info["lines"]:
        if s.startswith("switchport mode "):
            info["mode"] = s.split()[-1]
        elif s.startswith("switchport access vlan "):
            info["access"] = int(s.split()[-1])
        elif s.startswith("switchport trunk allowed vlan "):
            body = s.split("vlan ", 1)[1].strip()
            info["allowed"] = (set(ALL_VLANS) if body == "all"
                               else set() if body == "none" else parse_vlans(body))
        elif s.startswith("switchport trunk native vlan "):
            info["native"] = int(s.split()[-1])
        elif s == "shutdown":
            info["shutdown"] = True
    return info


# ---------- các loại kiểm tra: trả về (đạt?, mô tả yêu cầu, thực tế, gợi ý lệnh xem) ----------
CHECKS = {}


def check(name):
    def deco(fn):
        CHECKS[name] = fn
        return fn
    return deco


@check("vlan")
def c_vlan(m, d, c):
    got = d["vlans"].get(c["id"])
    want = c.get("name")
    ok = got is not None and (want is None or got == want)
    desc = f"{c['device']}: có VLAN {c['id']}" + (f" tên {want}" if want else "")
    return ok, desc, "chưa có VLAN này" if got is None else f"tên hiện tại: {got}", "show vlan brief"


@check("no_vlan")
def c_no_vlan(m, d, c):
    ok = c["id"] not in d["vlans"]
    return ok, f"{c['device']}: không còn VLAN {c['id']}", "VLAN vẫn tồn tại", "show vlan brief"


@check("port_vlan")
def c_port_vlan(m, d, c):
    bad = []
    for p in expand_ports(c["ports"]):
        i = port_info(d, p)
        ok = i["access"] == c["vlan"] and i["mode"] != "trunk" and (c["vlan"] == 1 or i["mode"] == "access")
        if not ok:
            bad.append(f"{p}(mode {i['mode'] or 'mặc định'}, vlan {i['access']})")
    return not bad, f"{c['device']}: {c['ports']} là access VLAN {c['vlan']}", "; ".join(bad), "show vlan brief"


@check("port_mode")
def c_port_mode(m, d, c):
    i = port_info(d, norm_port(c["port"]))
    return i["mode"] == c["mode"], f"{c['device']}: {c['port']} mode {c['mode']}", f"mode hiện tại: {i['mode'] or 'mặc định'}", "show interfaces trunk"


@check("trunk_allowed")
def c_trunk_allowed(m, d, c):
    i = port_info(d, norm_port(c["port"]))
    want = set(c["vlans"])
    return i["allowed"] == want, f"{c['device']}: {c['port']} cho phép VLAN {fmt_vlans(want)}", f"đang cho phép: {fmt_vlans(i['allowed'])}", "show interfaces trunk"


@check("port_shutdown")
def c_port_shutdown(m, d, c):
    i = port_info(d, norm_port(c["port"]))
    want = c.get("shutdown", True)
    word = "tắt (shutdown)" if want else "bật"
    return i["shutdown"] == want, f"{c['device']}: {c['port']} ở trạng thái {word}", f"shutdown = {i['shutdown']}", "show running-config"


@check("port_default")
def c_port_default(m, d, c):
    i = port_info(d, norm_port(c["port"]))
    return not i["lines"], f"{c['device']}: {c['port']} ở cấu hình mặc định", "còn dòng cấu hình: " + " | ".join(i["lines"]), "show running-config"


@check("enable_secret")
def c_enable_secret(m, d, c):
    return d["enable_secret"], f"{c['device']}: đã đặt enable secret", "chưa có enable secret", "show running-config"


@check("hostname")
def c_hostname(m, d, c):
    return d["hostname"] == c["name"], f"{c['device']}: hostname {c['name']}", f"hostname hiện tại: {d['hostname']}", "show running-config"


@check("ip")
def c_ip(m, d, c):
    ok = (c["ipv4"], c.get("mask", "255.255.255.0")) in d["ipv4"]
    return ok, f"{c['device']}: IPv4 {c['ipv4']} / {c.get('mask', '255.255.255.0')}", f"đang là: {d['ipv4'] or 'chưa đặt'}", "ipconfig"


@check("ipv6")
def c_ipv6(m, d, c):
    wants = c["ipv6"] if isinstance(c["ipv6"], list) else [c["ipv6"]]
    prefix = c.get("prefix", 64)
    ok = any((ipaddress.ip_address(w), prefix) == (ipaddress.ip_address(a), p)
             for w in wants for a, p in d["ipv6"] if a)
    return ok, f"{c['device']}: IPv6 {' hoặc '.join(wants)} /{prefix}", f"đang là: {[f'{a}/{p}' for a, p in d['ipv6']] or 'chưa đặt'}", "ipv6config"


def endpoints(c):
    a, b = (tuple(x.rsplit(":", 1)) for x in (c["a"], c["b"]))
    return frozenset([(a[0], norm_port(a[1])), (b[0], norm_port(b[1]))])


@check("link")
def c_link(m, d, c):
    return endpoints(c) in m["links"], f"cáp nối {c['a']} <-> {c['b']}", "không thấy cáp này", "xem lại topology"


@check("no_link")
def c_no_link(m, d, c):
    return endpoints(c) not in m["links"], f"không còn cáp {c['a']} <-> {c['b']}", "cáp vẫn còn", "xem lại topology"


# ---------- chạy ----------
def run(model, spec, step):
    passed = total = 0
    for c in spec["checks"]:
        if not (c.get("from", 1) <= step <= c.get("to", 99)):
            continue
        total += 1
        fn = CHECKS.get(c["type"])
        if fn is None:
            print(f"[BỎ QUA] loại kiểm tra không có: {c['type']}")
            continue
        dev = model["devices"].get(c.get("device")) if "device" in c else {}
        if dev is None:
            print(f"[SAI]  {c['type']} {c['device']}\n         -> không thấy thiết bị '{c['device']}' (kiểm tra tên hiển thị)")
            continue
        ok, desc, actual, hint = fn(model, dev, c)
        if ok:
            passed += 1
            print(f"[ĐẠT]  {desc}")
        else:
            print(f"[SAI]  {desc}\n         -> thực tế: {actual}   (xem bằng: {hint})")
    print(f"\nĐiểm: {passed}/{total}" + (f"  (bước {step})" if step < 99 else ""))
    return passed == total


def dump(model):
    print(f"Packet Tracer {model['version']}")
    for name, d in model["devices"].items():
        print(f"== {name} ({d['model']})  hostname={d['hostname']}  enable_secret={d['enable_secret']}")
        if d["vlans"]:
            print("   vlans:", {k: v for k, v in sorted(d["vlans"].items())})
        for p, lines in d["ports"].items():
            if lines:
                print(f"   {p}: {' | '.join(lines)}")
        if d["ipv4"] or d["ipv6"]:
            print("   ipv4:", d["ipv4"], " ipv6:", d["ipv6"])
    print("== links")
    for l in sorted(model["links"], key=str):
        a, b = sorted(l, key=str)
        print(f"   {a[0]}:{a[1]} <-> {b[0]}:{b[1]}")


def main():
    ap = argparse.ArgumentParser(description="Chấm bài Packet Tracer offline")
    ap.add_argument("file", help="file .pkt/.pka (hoặc .xml đã giải mã)")
    ap.add_argument("--lab", help="thư mục lab (chứa checks.json) hoặc đường dẫn checks.json")
    ap.add_argument("--step", type=int, help="chấm đến bước N (mặc định: bước cuối)")
    ap.add_argument("--dump", action="store_true", help="in những gì script đọc được từ file")
    a = ap.parse_args()

    model = build_model(load_xml(a.file))
    if a.dump:
        dump(model)
        return
    if not a.lab:
        sys.exit("Thiếu --lab (hoặc dùng --dump để xem nội dung file)")
    p = Path(a.lab)
    spec = json.loads((p / "checks.json" if p.is_dir() else p).read_text(encoding="utf-8"))
    step = a.step if a.step else spec.get("steps", 99)
    print(f"{spec.get('title', '')}  -  file: {Path(a.file).name}\n")
    sys.exit(0 if run(model, spec, step) else 1)


if __name__ == "__main__":
    main()
