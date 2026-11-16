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
    n = re.sub(r"(?i)^serial", "Se", n)
    n = re.sub(r"(?i)^se(?=\d)", "Se", n)
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
    """Đọc running-config: hostname, enable secret, cấu hình từng cổng, DHCP pool, tuyến."""
    cur, sec = None, None            # cur: cổng đang đọc; sec: (khóa, tên) của khối pool đang đọc
    for raw in lines:
        s = raw.strip()
        if raw.startswith("interface "):
            cur, sec = norm_port(raw.split(None, 1)[1]), None
            dev["ports"][cur] = []
        elif raw.startswith(" ") and cur:
            dev["ports"][cur].append(s)
        elif raw.startswith(" ") and sec:
            dev[sec[0]][sec[1]].append(s)
        else:
            cur, sec = None, None
            if s.startswith("ip dhcp pool ") or s.startswith("ipv6 dhcp pool "):
                key = "dhcp4_cfg" if s.startswith("ip dhcp") else "dhcp6_cfg"
                sec = (key, s.split()[-1])
                dev[key][sec[1]] = []
            elif s.startswith("ip dhcp excluded-address ") and len(s.split()) >= 4:
                p = s.split()
                dev["excluded"].append((p[3], p[4] if len(p) > 4 else p[3]))
            if s.startswith("hostname "):
                dev["hostname"] = s.split(None, 1)[1]
            elif s.startswith("enable secret"):
                dev["enable_secret"] = True
            elif s == "ipv6 unicast-routing":
                dev["ipv6_routing"] = True
            elif s.startswith("ip route ") and len(s.split()) >= 5:
                p = s.split()
                dev["routes4"].append((p[2], p[3], p[4]))      # (mạng, mask, next-hop)
            elif s.startswith("ipv6 route ") and len(s.split()) >= 4:
                p = s.split()
                dev["routes6"].append((p[2], p[3]))            # (prefix, next-hop)


def parse_device(eng):
    t = eng.find("TYPE")
    dev = {"model": t.get("model") if t is not None else None, "vlans": {},
           "hostname": None, "enable_secret": False, "ports": {},
           "ipv4": [], "ipv6": [], "ipv6_routing": False, "routes4": [], "routes6": [],
           "gateway4": None, "gateway6": None,
           "dhcp4_cfg": {}, "dhcp6_cfg": {}, "excluded": [], "dhcp_pools": [], "dhcp_enabled": False,
           "_eng": eng}
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
    # Pool DHCPv4 trên máy chủ nằm dưới DHCP_SERVERS/ASSOCIATED_PORTS/ASSOCIATED_PORT/DHCP_SERVER (theo từng cổng)
    for srv in eng.iterfind("DHCP_SERVERS//DHCP_SERVER"):
        dev["dhcp_enabled"] = dev["dhcp_enabled"] or srv.findtext("ENABLED") == "1"
        for p in srv.iterfind("POOLS/POOL"):
            dev["dhcp_pools"].append({"name": p.findtext("NAME"), "gateway": p.findtext("DEFAULT_ROUTER"),
                                      "dns": p.findtext("DNS_SERVER"), "start": p.findtext("START_IP"),
                                      "mask": p.findtext("MASK"), "max_users": p.findtext("MAX_USERS")})
    # Router không dây (WRT300N): IP phía LAN đặt trong GUI > Setup nên nằm ở thẻ riêng, không ở PORT
    lan_ip = eng.findtext(".//LAN_IP_ADDRESS")
    if lan_ip and lan_ip != "0.0.0.0":
        dev["ipv4"].append((lan_ip, eng.findtext(".//LAN_SUBNET_MASK")))
    for tag, key in (("GATEWAY", "gateway4"), ("IPV6_PORT_GATEWAY", "gateway6")):
        dev[key] = next((g.text.strip() for g in eng.iter(tag) if g.text and g.text.strip()), None)
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
            "shutdown": False, "ipv4": None, "ipv6": [], "lines": dev["ports"].get(port, [])}
    for s in info["lines"]:
        if s.startswith("ip address ") and len(s.split()) == 4:
            info["ipv4"] = (s.split()[2], s.split()[3])
        elif s.startswith("ipv6 address ") and "link-local" not in s and "/" in s:
            a, pl = s.split()[2].split("/")
            info["ipv6"].append((a, int(pl)))
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


@check("device")
def c_device(m, d, c):
    want = c.get("model")
    ok = want is None or d["model"] == want
    desc = f"có thiết bị {c['device']}" + (f" loại {want}" if want else "")
    return ok, desc, f"loại hiện tại: {d['model']}", "xem lại thiết bị trong workspace"


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
    mask = c.get("mask", "255.255.255.0")
    ok = any(a == c["ipv4"] and (mask is None or m == mask) for a, m in d["ipv4"])
    return ok, f"{c['device']}: IPv4 {c['ipv4']} / {mask or 'bất kỳ mask'}", f"đang là: {d['ipv4'] or 'chưa đặt'}", "ipconfig"


@check("ipv6")
def c_ipv6(m, d, c):
    wants = c["ipv6"] if isinstance(c["ipv6"], list) else [c["ipv6"]]
    prefix = c.get("prefix", 64)       # prefix: null = chấp nhận độ dài bất kỳ
    ok = any(ipaddress.ip_address(w) == ipaddress.ip_address(a) and (prefix is None or prefix == p)
             for w in wants for a, p in d["ipv6"] if a)
    return ok, f"{c['device']}: IPv6 {' hoặc '.join(wants)} /{prefix if prefix is not None else 'bất kỳ'}", f"đang là: {[f'{a}/{p}' for a, p in d['ipv6']] or 'chưa đặt'}", "ipv6config"


@check("gateway")
def c_gateway(m, d, c):
    bad = []
    if "ipv4" in c and d["gateway4"] != c["ipv4"]:
        bad.append(f"v4: {d['gateway4']}")
    if "ipv6" in c:
        g = d["gateway6"]
        if not (g and ipaddress.ip_address(g) == ipaddress.ip_address(c["ipv6"])):
            bad.append(f"v6: {g}")
    want = ", ".join(f"{k} {c[k]}" for k in ("ipv4", "ipv6") if k in c)
    return not bad, f"{c['device']}: default gateway {want}", "đang là " + "; ".join(bad), "ipconfig"


@check("ip_in")
def c_ip_in(m, d, c):
    net = ipaddress.ip_network(c["network"])
    ok = any(ipaddress.ip_address(a) in net for a, _ in d["ipv4"])
    return ok, f"{c['device']}: có IPv4 thuộc mạng {c['network']}", f"đang là: {d['ipv4'] or 'chưa có'}", "ipconfig"


@check("dhcp_pool")
def c_dhcp_pool(m, d, c):
    """DHCPv4 pool trên router (đọc từ running-config)."""
    lines = d["dhcp4_cfg"].get(c["name"])
    desc = f"{c['device']}: ip dhcp pool {c['name']}" + "".join(
        f", {k} {c[k]}" for k in ("network", "mask", "default_router", "dns_server") if k in c)
    if lines is None:
        return False, desc, "chưa có pool này", "show running-config"
    got = {ln.split(None, 1)[0]: (ln.split(None, 1) + [""])[1].split() for ln in lines if ln}
    bad = []
    if "network" in c and got.get("network") != [c["network"], c.get("mask", "255.255.255.0")]:
        bad.append(f"network {' '.join(got.get('network', [])) or '(chưa có)'}")
    for key, word in (("default_router", "default-router"), ("dns_server", "dns-server")):
        if key in c and c[key] not in got.get(word, []):
            bad.append(f"{word} {' '.join(got.get(word, [])) or '(chưa có)'}")
    return not bad, desc, "; ".join(bad), "show running-config"


@check("dhcp_excluded")
def c_dhcp_excluded(m, d, c):
    end = c.get("end", c["start"])
    return (c["start"], end) in d["excluded"], f"{c['device']}: excluded-address {c['start']} - {end}", f"đang là: {d['excluded'] or 'chưa loại trừ địa chỉ nào'}", "show running-config"


@check("dhcp6_pool")
def c_dhcp6_pool(m, d, c):
    lines = d["dhcp6_cfg"].get(c["name"])
    desc = f"{c['device']}: ipv6 dhcp pool {c['name']}" + (f", dns-server {c['dns_server']}" if "dns_server" in c else "")
    if lines is None:
        return False, desc, "chưa có pool này", "show running-config"
    ok = "dns_server" not in c or any(c["dns_server"] in ln.split() for ln in lines if ln.startswith("dns-server"))
    return ok, desc, f"các dòng trong pool: {lines}", "show running-config"


@check("port_line")
def c_port_line(m, d, c):
    """Cổng có đúng một dòng cấu hình (ví dụ ip helper-address, ipv6 dhcp server ...)."""
    i = port_info(d, norm_port(c["port"]))
    ok = any(ln.lower() == c["line"].lower() for ln in i["lines"])
    return ok, f"{c['device']}: {c['port']} có dòng '{c['line']}'", f"các dòng hiện có: {i['lines']}", "show running-config"


@check("dhcp_server_pool")
def c_dhcp_server_pool(m, d, c):
    """DHCPv4 pool cấu hình trên máy chủ (Services > DHCP)."""
    pool = next((p for p in d["dhcp_pools"] if p["name"] == c["name"]), None)
    keys = [k for k in ("gateway", "dns", "start", "mask", "max_users") if k in c]
    desc = f"{c['device']}: DHCP server bật, pool {c['name']}" + "".join(f", {k} {c[k]}" for k in keys)
    if pool is None:
        return False, desc, "chưa có pool tên này", "Services > DHCP"
    bad = [f"{k}: {pool[k]}" for k in keys if str(pool[k]) != str(c[k])]
    if not d["dhcp_enabled"]:
        bad.append("dịch vụ DHCP đang Off")
    return not bad, desc, "; ".join(bad), "Services > DHCP"


@check("xml_value")
def c_xml_value(m, d, c):
    """Giá trị một thẻ trong cấu hình thiết bị, ví dụ DNS_SERVER/ENABLED = 1."""
    el = d["_eng"].find(c["path"])
    val = el.text.strip() if el is not None and el.text else None
    return val == str(c["equals"]), f"{c['device']}: {c['label']}", f"{c['path']} = {val}", "mở tab Services của máy chủ"


@check("xml_has")
def c_xml_has(m, d, c):
    """Cấu hình dịch vụ có chứa các chuỗi (không phân biệt hoa thường). Chỉ so chuỗi, không phân biệt loại bản ghi."""
    root = d["_eng"].find(c["path"]) if c.get("path") else d["_eng"]
    text = " ".join(ET.tostring(root, encoding="unicode").split()).lower() if root is not None else ""
    missing = [x for x in c["contains"] if x.lower() not in text]
    return not missing, f"{c['device']}: {c['label']}", f"chưa thấy: {missing}", "mở tab Services của máy chủ"


def endpoints(c):
    a, b = (tuple(x.rsplit(":", 1)) for x in (c["a"], c["b"]))
    return frozenset([(a[0], norm_port(a[1])), (b[0], norm_port(b[1]))])


@check("link")
def c_link(m, d, c):
    return endpoints(c) in m["links"], f"cáp nối {c['a']} <-> {c['b']}", "không thấy cáp này", "xem lại topology"


@check("no_link")
def c_no_link(m, d, c):
    return endpoints(c) not in m["links"], f"không còn cáp {c['a']} <-> {c['b']}", "cáp vẫn còn", "xem lại topology"


@check("port_ip")
def c_port_ip(m, d, c):
    i = port_info(d, norm_port(c["port"]))
    want4 = (c["ipv4"], c["mask"]) if "ipv4" in c else None
    ok = want4 is None or i["ipv4"] == want4
    if "ipv6" in c:
        w6 = (ipaddress.ip_address(c["ipv6"]), c.get("prefix", 64))
        ok = ok and any((ipaddress.ip_address(a), p) == w6 for a, p in i["ipv6"])
    want = " ".join(x for x in (f"{c['ipv4']} {c['mask']}" if want4 else "", f"{c['ipv6']}/{c.get('prefix', 64)}" if "ipv6" in c else "") if x)
    return ok, f"{c['device']}: {c['port']} có {want}", f"đang là: v4 {i['ipv4']}, v6 {i['ipv6']}", "show ip interface brief"


@check("port_up")
def c_port_up(m, d, c):
    i = port_info(d, norm_port(c["port"]))
    return not i["shutdown"], f"{c['device']}: {c['port']} đã bật (no shutdown)", "cổng đang shutdown", "show ip interface brief"


@check("ipv6_routing")
def c_ipv6_routing(m, d, c):
    return d["ipv6_routing"], f"{c['device']}: đã bật ipv6 unicast-routing", "chưa bật", "show running-config"


def connected(dev, ver):
    """Các mạng nối trực tiếp của router (cổng đang bật): [(network, tên cổng, địa chỉ cổng)]."""
    out = []
    for name in dev["ports"]:
        i = port_info(dev, name)
        if i["shutdown"]:
            continue
        if ver == 4 and i["ipv4"]:
            net = ipaddress.ip_interface(f"{i['ipv4'][0]}/{i['ipv4'][1]}")
            out.append((net.network, name, net.ip))
        if ver == 6:
            for a, p in i["ipv6"]:
                net = ipaddress.ip_interface(f"{a}/{p}")
                out.append((net.network, name, net.ip))
    return out


def trace(m, start, dest):
    """Đi theo bảng định tuyến (kết nối + tĩnh + mặc định). Trả về (thành công?, lý do/đường đi)."""
    dest = ipaddress.ip_address(dest)
    ver = dest.version
    cur, path = start, [start]
    for _ in range(16):
        dev = m["devices"][cur]
        if any(dest in net for net, _, _ in connected(dev, ver)):
            return True, " -> ".join(path)
        if ver == 6 and not dev["ipv6_routing"]:
            return False, f"{cur} chưa bật ipv6 unicast-routing nên không chuyển tiếp IPv6 (đường đi: {' -> '.join(path)})"
        routes = []
        for r in (dev["routes4"] if ver == 4 else dev["routes6"]):
            try:
                net = (ipaddress.ip_network(f"{r[0]}/{r[1]}") if ver == 4 else ipaddress.ip_network(r[0]))
                nh = ipaddress.ip_address(r[-1])
            except ValueError:
                continue    # next-hop dạng tên cổng: chưa hỗ trợ
            if dest in net:
                routes.append((net.prefixlen, nh))
        if not routes:
            return False, f"{cur} không có tuyến tới {dest} (đường đi: {' -> '.join(path)})"
        _, nh = max(routes, key=lambda x: x[0])
        if not any(nh in net for net, _, _ in connected(dev, ver)):
            return False, f"{cur}: next-hop {nh} không thuộc mạng nào nối trực tiếp (hoặc cổng đang shutdown)"
        owner = next((n for n, dv in m["devices"].items() if n != cur
                      and any(a == nh for _, _, a in connected(dv, ver))), None)
        if owner is None:
            return False, f"{cur}: không router nào có địa chỉ {nh} (next-hop sai hoặc cổng kia đang tắt)"
        cur = owner
        if cur in path:
            return False, f"vòng lặp định tuyến: {' -> '.join(path + [cur])}"
        path.append(cur)
    return False, "vượt quá 16 chặng"


@check("reach")
def c_reach(m, d, c):
    ok, why = trace(m, c["device"], c["dest"])
    return ok, f"{c['device']} định tuyến được tới {c['dest']}", why, "show ip route / show ipv6 route"


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
        if d["routes4"] or d["routes6"] or d["ipv6_routing"]:
            print("   ipv6_routing:", d["ipv6_routing"], " ip route:", d["routes4"], " ipv6 route:", d["routes6"])
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
